
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <string.h>
#include <time.h>

#include <net/ethernet.h>
#include <netinet/ip.h>
#include <netinet/ip6.h>
#include <netinet/udp.h>	
#include <netinet/tcp.h>
#include <netdb.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <getopt.h>
#include <pcap.h> 
#include <errno.h>


void print_packet_info(const u_char *packet, struct pcap_pkthdr packet_header);
void packet_handler(u_char *args, const struct pcap_pkthdr *packet_header, const u_char *packet_body);
void print_packet(const u_char * data , int Size);
void print_data (const u_char * data , int Size, int len);


struct option long_options[] =
{
  {"tcp", no_argument, NULL, 't'},
  {"udp",  no_argument, NULL, 'u'},
  {0, 0, 0, 0}  
};

char * short_options = "i:p:n:tuh";

char interface[50];
bool h = true;

int main(int argc, char **argv)
{
    struct bpf_program fp;

	int opt;
    int option_index = 0;

   
    char filter[50];
    char port[10];

    memset(interface, 0, 50);
    memset(filter, 0, 50);
    memset(port, 0, 10);

    int packet_count = 1;
    bool tcp = false;
    bool udp = false;
    
	while((opt = getopt_long(argc, argv, short_options, long_options, &option_index)) != -1) // zpracovani argumentu
    {  
        switch(opt)  
        {  
            case 'i':
                strcpy(interface, optarg);  
                break;  
            case 'p':  
                 strcpy(port, optarg); 
                break;  
            case 'n': 
                packet_count = atoi(optarg);
                break;  
            case 't':
                strcpy(filter, "tcp ");
                tcp = true;
                break;
            case 'h':
                h = false;
                break;
            case 'u':
                strcpy(filter, "udp ");
               
                udp = true;
                break;
        }  
    } 
    if((tcp == false && udp == false) || (tcp == true && udp == true))
    {
        strcpy(filter,"");
    }
    if(strlen(port) != 0)
    {
        if(atoi(port) < 0 || atoi(port) > 65535)
        {
            fprintf(stderr, "Spatny port\n");
            exit(1);
        }

        strcat(filter, "port ");
        strcat(filter, port);
    }
    
    
    pcap_if_t * alldevices, * device;
	pcap_t * handler; 

	char errbuf[100] , *devname;

	int count = 1 , n;


    if(pcap_findalldevs( &alldevices , errbuf)) // funkce nalezne vsechna rozhrani
	{
		fprintf(stderr, "Chyba pri hledani rozhrani %s" , errbuf);
		exit(1);
	}

    if(strlen(interface) == 0) //pokud nebyl zadan parametr -i tak se zobrazi vsechna rozhrani
    {
        for(device = alldevices; device != NULL; device = device->next)
        {
            printf("%d. %s - %s\n", count, device->name, device->description);
            count++;
        }

        return 0;
    }

    handler = pcap_open_live(interface, 2000, 1, 0, errbuf); //otevreni session pro zadany interface

    if(handler == NULL)
    {
        fprintf(stderr, "Chyba pri otevirani rozhrani %s" , errbuf);
		exit(1);
    }


    if(pcap_compile(handler, &fp, filter, 1, PCAP_NETMASK_UNKNOWN) == -1) //parsovani filtru pro pcap (port 80, tcp, udp port 23, atd...)
    {
        fprintf(stderr, "Chyba pri parsovani filtru %s", filter);
		exit(1);
    }
    if(pcap_setfilter(handler, &fp) == -1)
    {
        fprintf(stderr, "Chyba pri nastavovani filtru %s", filter); // nastaveni filtru pro pcap
		exit(1);
    }

    pcap_loop(handler, packet_count, packet_handler, NULL); // zpracovani paketu (packet_count rika kolik se vezme packetu)



    pcap_freecode(&fp); // zaverecny uklid
	pcap_close(handler);

    return 0;
}



void packet_handler(u_char *args, const struct pcap_pkthdr *packet_header, const u_char *packet_body)
{
    struct sockaddr_in addr;
    struct sockaddr_in6 addr6;

    char hostbuffer_src[256];
    char hostbuffer_dst[256];

    memset(hostbuffer_src, 0, 256);
    memset(hostbuffer_dst, 0, 256);

    u_char * printable;
    int total_size;
    int ether_or_lin_cook;
    int size_ip_header;
    int protocol;

    if(strcmp(interface,"any") == 0)
        ether_or_lin_cook = 16; //pokud jsme na rozhrani any tak je misto ethernetu 16 bytovy linux cooked capture
    else
        ether_or_lin_cook = 14;
        
    struct ip * ip_header = (struct ip *)(packet_body + ether_or_lin_cook); // namapovani packetu na ip hlavicku, je zde posun 14 bytu (velikost ethernetove hlavicky nebo linux cooked capture)
    struct ip6_hdr * ip6_header = (struct ip6_hdr *)(packet_body + ether_or_lin_cook);


    if((int)ip_header->ip_v == 6) // ipv6
    {
        size_ip_header = 40; // ipv6 fixed header je 40 bytu dlouhy
        
        protocol = (int) ip6_header->ip6_ctlun.ip6_un1.ip6_un1_nxt; // zjisteni protokolu
    }  
    else // ipv4
    {
        size_ip_header = (int)(ip_header->ip_hl * 4); //delka ip_headeru * 4 (jednotka je 4 bytovy word)

        protocol = (int) ip_header->ip_p; // zjisteni protokolu
    }
        
    
    struct tm ts;
    char buf[80], usec_buf[7];

    // prevod mikrosekund na zobrazitelne cislo
    ts = *localtime(&(packet_header->ts.tv_sec)); 
    strftime(buf, sizeof(buf), "%H:%M:%S", &ts); 
    strcat(buf,".");
    sprintf(usec_buf,"%6d", (int) packet_header->ts.tv_usec);
    strcat(buf, usec_buf);



    if(h) // h je parametr z prikazove radky
    {
         // preklad src ip adresy na src hostname, pokud se hostname nepodari zjistit tak se necha ip adresa

        if((int)ip_header->ip_v == 6) // ipv6
        {
            addr6.sin6_family = AF_INET6;
            addr6.sin6_addr = ip6_header->ip6_src;
            if(getnameinfo((struct sockaddr *) &addr6, sizeof(struct sockaddr), hostbuffer_src, 255, NULL, 0, NI_NAMEREQD) != 0);
            {
                if(hostbuffer_src[0] == 0)
                    inet_ntop(AF_INET6, &(ip6_header->ip6_src), hostbuffer_src, sizeof(hostbuffer_src));
            }
        }
        else //ipv4
        {
            addr.sin_family = AF_INET;
            addr.sin_addr = ip_header->ip_src;
            if(getnameinfo((struct sockaddr *) &addr, sizeof(struct sockaddr), hostbuffer_src, 255, NULL, 0, NI_NAMEREQD) != 0);
            {
                if(hostbuffer_src[0] == 0)
                    strcpy(hostbuffer_src, inet_ntoa(addr.sin_addr));
            }
        }

        // preklad dst ip adresy na dst hostname, pokud se hostname nepodari zjistit tak se necha ip adresa
        
        if((int)ip_header->ip_v == 6) //ipv6
        {
            addr6.sin6_addr = ip6_header->ip6_dst;
            if(getnameinfo((struct sockaddr *) &addr6, sizeof(struct sockaddr), hostbuffer_dst, 255, NULL, 0, NI_NAMEREQD) != 0);
            {
                if(hostbuffer_dst[0] == 0)
                    inet_ntop(AF_INET6, &(ip6_header->ip6_dst), hostbuffer_dst, sizeof(hostbuffer_dst));
            }
        }
        else // ipv4
        {
            addr.sin_addr = ip_header->ip_dst;
            if(getnameinfo((struct sockaddr *) &addr, sizeof(struct sockaddr_in), hostbuffer_dst, 255, NULL, 0, NI_NAMEREQD) != 0);
            {
                if(hostbuffer_dst[0] == 0)
                    strcpy(hostbuffer_dst, inet_ntoa(addr.sin_addr));
            }
        }
    }
    else // necha se ip adresa
    {   
      
        if((int)ip_header->ip_v == 6) // ulozeni src ipv6 adresy
        {
            inet_ntop(AF_INET6, &(ip6_header->ip6_src), hostbuffer_src, sizeof(hostbuffer_src));
        }
        else // ulozeni src ipv4 adresy
        {
            addr.sin_family = AF_INET;
            addr.sin_addr = ip_header->ip_src;
            strcpy(hostbuffer_src, inet_ntoa(addr.sin_addr));
        }
        
        if((int)ip_header->ip_v == 6) // ulozeni dst ipv6 adresy
        {
            inet_ntop(AF_INET6, &(ip6_header->ip6_dst), hostbuffer_dst, sizeof(hostbuffer_dst));
        }
           
        else // ulozeni dst ipv4 adresy
        {
            addr.sin_addr = ip_header->ip_dst;
            strcpy(hostbuffer_dst, inet_ntoa(addr.sin_addr));
        }
    }



    if(protocol == 6) // pokud je protocol tcp
    {
        struct tcphdr * tcp_header = (struct tcphdr *) (packet_body + size_ip_header + ether_or_lin_cook); // namapovani packetu na tcp header, je zde posun o ethernetovou a ip hlavicku
        int size_tcp_header = (int) tcp_header->th_off * 4; //delka tcp_headeru * 4 (jednotka je 4 bytovy word)

        printable = (u_char *) (packet_body);

        if((int)ip_header->ip_v == 6) // ipv6
        {
            total_size = ether_or_lin_cook + size_ip_header + size_tcp_header;
        }
        else // ipv4
        {
             // ethernet nebo linux c. cap. + ip_hlavicka + tcp_hlavicka + zbytek dat
            total_size = ether_or_lin_cook + size_ip_header + size_tcp_header + (ntohs(ip_header->ip_len) - (size_ip_header + size_tcp_header)); 
        }
        
       
        printf("%s %s : %u > %s : %u\n\n",buf, hostbuffer_src, ntohs(tcp_header->th_sport), hostbuffer_dst, ntohs(tcp_header->th_dport));
        
        print_packet (printable, total_size);

        printf("\n");
    }
    else // jinak je udp
    {

        struct udphdr * udp_header = (struct udphdr *) (packet_body + size_ip_header + ether_or_lin_cook); // namapovani packetu na udp header, je zde posun o ethernetovou a ip hlavicku

        printable = (u_char *) (packet_body);

        if((int)ip_header->ip_v == 6) // ipv6
        {
            total_size = ether_or_lin_cook + size_ip_header + 8;
        }
        else // ipv4
        {
            // ethernet nebo linux c. cap. + ip_hlavicka + udp_hlavicka (8 bytu) + zbytek dat
            total_size = ether_or_lin_cook + size_ip_header + 8 + (ntohs(ip_header->ip_len) - (size_ip_header + 8)); 
        }
        printf("%s %s : %u > %s : %u\n\n",buf, hostbuffer_src, ntohs(udp_header->uh_sport), hostbuffer_dst, ntohs(udp_header->uh_dport));

        print_packet (printable, total_size);

        printf("\n");

    }

    return;
}



void print_packet(const u_char * data , int Size)
{
    int line_rem = Size;
    int byte_size = 0;
    int line_length;

    int row_count = 0;


    if(Size <= 16) //pokud se celkova delka vypisu vleze na jeden radek
    {
        print_data(data, byte_size, Size);
    }
    else
    {
       while(1)
        {
            line_length = 16 % Size;

            if(line_length == 16) //vypis cely radek (16 bytu) 
            {
                print_data(data, byte_size, 16);
                
                Size = Size - 16;
                data = data + 16;
                byte_size = byte_size + 16;
            }
                
            else // nakonec vypis zbytek
            {
                line_length = Size;
                print_data(data, byte_size, line_length);
                break;
            }
        }
    }
}

// funkce pro samotny vypis dat
void print_data (const u_char * data , int Size, int len)
{
	int i;

    printf("0x%05x:  ", Size);

	for(i = 0 ;i < len ;i++) // vypis bytu v hex
	{  
        printf("%02x ",data[i]);
        if(i == 7) // prostredni mezera po 8 bytech
        {
            printf("  ");
        }
        
    }
   
	if (len < 16) // vyplneni mezerami pokud neni radek cely
    {
        if (len < 8)
		    printf("  ");
		for (i = 0; i < 16-len; i++) 
        {
			printf("   ");
		}
    }


	for(i = 0; i < len; i++)
    {
        if(data[i] >= 32 && data[i] <= 126) //pokud je znak tisknutelny tak ho vypis, jestli ne vypise se tecka
        {
            printf("%c", data[i]);
        }
        else 
        {
            printf(".");
        }
    }
    
    printf("\n");

			
}
        
	
