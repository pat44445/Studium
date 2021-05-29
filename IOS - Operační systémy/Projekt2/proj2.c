#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <semaphore.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/shm.h>
#include <sys/sem.h>
#include <sys/wait.h>
#include <sys/ipc.h>
#include <time.h>




#define HACKER 0
#define SERF 1





typedef struct // struktura pro ulozeni parametru
{
    int p; //pocet procesu
    int h; //hodnota doby generovani procesu hackers
    int s; //hodnota doby generovani procesu serfs
    int r; //maximalni hodnota plavby
    int w; //max hodnota po kterou se osoba vraci na molo
    int c; //kapacita mole

}parametry;





// Deklarace semaforu
sem_t
    *sem_citac = NULL,
    *sem_log_soub = NULL,
    *sem_molo = NULL,
    *sem_kap_molo = NULL,
    *sem_board = NULL,
    *sem_plavba = NULL,
    *sem_hacker = NULL,
    *sem_serf = NULL,
    *sem_pristani = NULL,
    *sem_konec= NULL;


int pam_0, pam_1, pam_2, pam_3; // deklarace file descriptoru

int *sd_pam_citac, *sd_pam_hackers, *sd_pam_serfs, *sd_pam_lod; // deklarace sdilene pameti





FILE *log_soub = NULL; // Deklarace vystupniho souboru




// Hlavicky k funkcim
int vyber_posadky(void);
int citani(int *sd_pam, int y);
int child_proces(FILE *log_soub, parametry *par, int kategorie, int i, int *pam_citac);
int hlavni_proces(FILE *log_soub, parametry *par, int pauza, int kategorie);
int init_semaforu_a_sd_pam(void);
int smazani_semaforu_a_sd_pam(void);
int kontrola_parametru(int argc,char *argv[], parametry *par);
void odemceni_semaf(sem_t *semaf, int kolik);





enum // vycet jmen pro chybove hlasky
{
    pocet_arg,
    prvni_arg,
    dvatrictyri_arg,
    paty_arg,
    sesty_arg,
    neni_cele_cislo,
    semaf_chyba,
    soub_chyba,
    chyba_procesu,
    sd_pam,
    mp_pam,
    fork_procesu,
    smaz_semaf,
    smaz_sd_pam,
    odmap_pam,
    cls_file_des,
    cls_file,
    zav_semaf,
};


const char *vypis_chyby[] = // seznam chybovych hlasek
{
    [pocet_arg]="Nespravny pocet argumentu.\n",
    [prvni_arg]="Pocet osob je mensi nez dva nebo pocet osob neni sude cislo.\n",
    [dvatrictyri_arg]="Spatna hodnota doby po kterou je generovan proces.\n",
    [paty_arg]="Spatna hodnota doby po ktere se osoba vraci zpet na molo.\n",
    [sesty_arg]="Kapacita mola je mensi nez 5.\n",
    [neni_cele_cislo]="Nektery z parametru neni cele cislo.\n",
    [semaf_chyba]="Nepodarilo se otevrit semafor(y)\n",
    [soub_chyba]="Nepodarilo se otevrit vystupni soubor\n",
    [chyba_procesu]="Pri generovani procesu doslo k chybe\n",
    [sd_pam]="Nepodarilo se vytvoritt sdilenou pamet\n",
    [mp_pam]="Namapovani sdilene pameti se nepodarilo\n",
    [fork_procesu]="Forkovani childprocesu se nepodarilo\n",
    [smaz_semaf]="Smazani semaforu se nepodarilo\n",
    [smaz_sd_pam]="Smazani sdilene pameti se nepodarilo\n",
    [odmap_pam]="Odmapovani sdilene pameti se nepodarilo\n",
    [cls_file_des]="Zavreni file descriptoru se nepodarilo\n",
    [cls_file]="Zavreni souboru se nepodarilo\n",
    [zav_semaf]="Zavreni semaforu se nepodarilo\n",
};

// Pole pro vypis do souboru: 2 retezce, HACK nebo SERF
const char *hacker_or_serf[] =
{
    [HACKER]="HACK",
    [SERF]="SERF",

};


int main(int argc, char *argv[])
{

    parametry *par, init;
    par = &init; // vytvoreni ukazatele na strukturu parametry



    pid_t pid_hacker, pid_serf; // Deklarace pid procesu

    srand(time(NULL)); // Pro generovani nahodnych cisel




    if(kontrola_parametru(argc, argv, par) == -1) // Kontrola spravnosti parametru
        return 1;


    if ((log_soub = fopen("proj2.out", "w+")) == NULL)  // Otevreni souboru
    {
        fprintf(stderr, "%s", vypis_chyby[soub_chyba]);
        return 1;
    }

    setbuf(log_soub, NULL); // pro spravny vystup do souboru


    if((init_semaforu_a_sd_pam()) == -1) // Kontrola jestli se podarila inicializace semaforu a sdilenych pameti
    {
        smazani_semaforu_a_sd_pam();
        return 1;
    }



    // Inicializace promenych - sdilene pameti a nastaveni jeji hodnoty na nula
    *sd_pam_citac = 0;
    *sd_pam_hackers = 0;
    *sd_pam_lod = 0;
    *sd_pam_serfs = 0;



    pid_hacker = fork(); // fork procesu hacker

    if(pid_hacker == 0)
    {
         if(hlavni_proces(log_soub, par, par-> h, HACKER) == -1) // pokud se v fukcich neco nepodarilo tak konec
         {
            fprintf(stdout, "%s", vypis_chyby[chyba_procesu]);
            smazani_semaforu_a_sd_pam();
            return -1;
         }
    }

    else if(pid_hacker < 0) // pokud se fork nepodaril tak konec
    {
        return 1;
    }

    pid_serf = fork(); // fork procesu serf

    if(pid_serf == 0)
    {
         if(hlavni_proces(log_soub, par, par-> s, SERF) == -1) // pokud se v fukcich neco nepodarilo tak konec
         {
            fprintf(stdout, "%s", vypis_chyby[chyba_procesu]);
            smazani_semaforu_a_sd_pam();
            return -1;
         }
    }

    else if(pid_serf < 0) // pokud se fork nepodaril tak konec
    {
        return 1;
    }



    int child_proc;

    // ujisteni z vsechny funkce se ukoncili
    for (child_proc = 0; child_proc < ((par -> p) * 2 + 2); child_proc ++)
    {
        wait(NULL);
    }

    waitpid(-1, NULL, 0);


    smazani_semaforu_a_sd_pam(); // na konec se smazou vsechny sdilene zdroje

    return 0;
}

int kontrola_parametru(int argc,char *argv[], parametry *par)
{
    char *chyba;
    int cislo;

    if(argc != 7) //Kontrola poctu argumentu
    {
        fprintf(stderr,"%s",vypis_chyby[pocet_arg]);
        return -1;
    }

    for(int i = 1; i < 7; i++) // Kontrola jestli jsou argumenty int
    {
        strtoul(argv[i],&chyba,10);
        if(*chyba != '\0')
        {
            fprintf(stderr,"%s",vypis_chyby[neni_cele_cislo]);
            return -1;
        }
    }

    cislo=strtoul(argv[1],&chyba,10);
    if(cislo < 2 || cislo%2 != 0) // Kontrola spravnosti prvniho argumentu
    {
        fprintf(stderr,"%s",vypis_chyby[prvni_arg]);
        return -1;
    }
    par->p = cislo; // zapis do struktury parametry


    for(int i=2; i < 5; i++) // Kontrola spravnosti druheho, tretiho a ctvrteho argumentu
    {
        cislo=strtoul(argv[i],&chyba,10);
        if(cislo < 0 || cislo > 2000)
        {
            fprintf(stderr,"%s",vypis_chyby[dvatrictyri_arg]);
            return -1;
        }
    }
    par->h=strtoul(argv[2],&chyba,10); // zapis do struktury parametry
    par->s=strtoul(argv[3],&chyba,10);
    par->r=strtoul(argv[4],&chyba,10);


    cislo=strtoul(argv[5],&chyba,10);
    if(cislo < 20 || cislo > 2000) // Kontrola spravnosti pateho argumentu
    {
        fprintf(stderr,"%s",vypis_chyby[paty_arg]);
        return -1;
    }
    par->w=cislo; // zapis do struktury parametry


    cislo=strtoul(argv[6],&chyba,10);
    if(cislo < 5) // Kontrola spravnosti sesteho argumentu
    {
        fprintf(stderr,"%s",vypis_chyby[sesty_arg]);
        return -1;
    }
    par->c=cislo; // zapis do struktury parametry

    return 0;
}


int init_semaforu_a_sd_pam(void)
{
    // otevreni semaforu

    // cislo na konci znamena pro kolik procesu je ze zacatku otevreny, pokud je nula tak se semafor otevre
    //az po splneni nejake podminky

    // O_CREAT = flag pro vytvoreni
    // O_EXCL = flag pro exkluzivitu
    // 0644 = nastaveni pristupovych prav
    if (
             ((sem_citac = sem_open("/xdvora3dsemafor_citac", O_CREAT | O_EXCL, 0644, 1)) == SEM_FAILED)
          || ((sem_log_soub = sem_open("/xdvora3dsemafor_log_soub", O_CREAT | O_EXCL, 0644, 1)) == SEM_FAILED)
          || ((sem_molo =sem_open("/xdvora3dsemafor_molo", O_CREAT | O_EXCL, 0644, 1)) == SEM_FAILED)
          || ((sem_kap_molo =sem_open("/xdvora3dsemafor_kap_molo", O_CREAT | O_EXCL, 0644, 4)) == SEM_FAILED)
          || ((sem_hacker =sem_open("/xdvora3dsemafor_hacker", O_CREAT | O_EXCL, 0644, 0)) == SEM_FAILED)
          || ((sem_serf =sem_open("/xdvora3dsemafor_serf", O_CREAT | O_EXCL, 0644, 0)) == SEM_FAILED)
          || ((sem_board = sem_open("/xdvora3dsemafor_board", O_CREAT | O_EXCL, 0644, 0)) == SEM_FAILED)
          || ((sem_plavba = sem_open("/xdvora3dsemafor_plavba", O_CREAT | O_EXCL, 0644, 0)) == SEM_FAILED)
          || ((sem_pristani = sem_open("/xdvora3dsemafor_pristani", O_CREAT | O_EXCL, 0644, 0)) == SEM_FAILED)
          || ((sem_konec = sem_open("/xdvora3dsemafor_konec", O_CREAT | O_EXCL, 0644, 1)) == SEM_FAILED) )
            {
                fprintf(stderr,"%s",vypis_chyby[semaf_chyba]);
                return -1;
            }



          // Vytvoreni sdilene pameti
          // O_RWDR = prava pro cteni a zapis
    if (     ((pam_0 = shm_open("/xdvora3dpamet0", O_CREAT | O_EXCL | O_RDWR, 0644)) == -1)
          || ((pam_1 = shm_open("/xdvora3dpamet1", O_CREAT | O_EXCL | O_RDWR, 0644)) == -1)
          || ((pam_2 = shm_open("/xdvora3dpamet2", O_CREAT | O_EXCL | O_RDWR, 0644)) == -1)
          || ((pam_3 = shm_open("/xdvora3dpamet3", O_CREAT | O_EXCL | O_RDWR, 0644)) == -1)
       )
            {
                fprintf(stderr,"%s",vypis_chyby[sd_pam]);
                return -1;
            }

    // uprava velikosti file_descriptoru na velikost jednoho integeru
    if (    (ftruncate(pam_0, sizeof(int)) == -1) || (ftruncate(pam_1, sizeof(int)) == -1)
         || (ftruncate(pam_2, sizeof(int)) == -1) || (ftruncate(pam_3, sizeof(int)) == -1)
       )
    {

        return -1;
    }

          //namapovani sdilene pameti

    if (     ((sd_pam_citac = mmap(NULL, sizeof(int), PROT_READ | PROT_WRITE, MAP_SHARED, pam_0, 0)) == MAP_FAILED)
          || ((sd_pam_hackers = mmap(NULL, sizeof(int), PROT_READ | PROT_WRITE, MAP_SHARED, pam_1, 0)) == MAP_FAILED)
          || ((sd_pam_serfs = mmap(NULL, sizeof(int), PROT_READ | PROT_WRITE, MAP_SHARED, pam_2, 0)) == MAP_FAILED)
          || ((sd_pam_lod = mmap(NULL, sizeof(int), PROT_READ | PROT_WRITE, MAP_SHARED, pam_3, 0)) == MAP_FAILED)
       )
            {
                fprintf(stderr, "%s", vypis_chyby[mp_pam]);
                return -1;
            }


    return 0;

}

int smazani_semaforu_a_sd_pam(void)
{
    int chyba = 0;

    // Zavreni vsech semaforu

    if (    (sem_close(sem_citac) == -1) || (sem_close(sem_log_soub) == -1) || (sem_close(sem_plavba) == -1)
         || (sem_close(sem_molo) == -1) || (sem_close(sem_kap_molo) == -1) || (sem_close(sem_hacker) == -1)
         || (sem_close(sem_serf) == -1) || (sem_close(sem_board) == -1) || (sem_close(sem_pristani) == -1)
         || (sem_close(sem_konec) == -1)
       )
    {
        fprintf(stderr, "%s", vypis_chyby[zav_semaf]);
        chyba = -1;
    }

    // Smazani vsech semaforu z /dev/shm

    if (    (sem_unlink("/xdvora3dsemafor_citac") == -1) || (sem_unlink("/xdvora3dsemafor_log_soub") == -1)
         || (sem_unlink("/xdvora3dsemafor_molo") == -1) || (sem_unlink("/xdvora3dsemafor_kap_molo") == -1)
         || (sem_unlink("/xdvora3dsemafor_hacker") == -1) || (sem_unlink("/xdvora3dsemafor_serf") == -1)
         || (sem_unlink("/xdvora3dsemafor_board") == -1) || (sem_unlink("/xdvora3dsemafor_plavba") == -1)
         || (sem_unlink("/xdvora3dsemafor_pristani") == -1) || (sem_unlink("/xdvora3dsemafor_konec") == -1)   )
    {
        fprintf(stderr, "%s", vypis_chyby[smaz_semaf]);
        chyba = -1;
    }

    // Odmapovani sdilene pameti

    if (    ((munmap(sd_pam_citac, sizeof(int))) != 0) || ((munmap(sd_pam_hackers, sizeof(int))) != 0)
         || ((munmap(sd_pam_serfs, sizeof(int))) != 0) || ((munmap(sd_pam_lod, sizeof(int))) != 0)
       )
    {
        fprintf(stderr, "%s", vypis_chyby[odmap_pam]);
        chyba = -1;
    }

    // smazani sdilene pameti z /dev/shm

    if (    (shm_unlink("/xdvora3dpamet0") == -1) || (shm_unlink("/xdvora3dpamet1") == -1)
         || (shm_unlink("/xdvora3dpamet2") == -1) || (shm_unlink("/xdvora3dpamet3") == -1)
       )
    {
        fprintf(stderr, "%s", vypis_chyby[smaz_sd_pam]);
        chyba = -1;
    }

    // Zavreni file descriptoru

    if (    (close(pam_0) == -1) || (close(pam_1) == -1)
         || (close(pam_2) == -1) || (close(pam_3) == -1)
       )
    {
        fprintf(stderr, "%s", vypis_chyby[cls_file_des]);
        chyba = -1;
    }

    // Zavreni vstupniho souboru

    if (fclose(log_soub) == EOF)
    {
        fprintf(stderr, "%s", vypis_chyby[cls_file]);
        chyba = -1;
    }



    return chyba;
}








int hlavni_proces(FILE *log_soub, parametry *par, int pauza, int kategorie)
{

    pid_t pid_child;
    int i = 0;

    while(i < par-> p) // pro pocet generovanych procesu delej
    {
        i++;
        if(pauza != 0)
            usleep((random() % (pauza))*1000); //uspani na dobu z intervalu, pokud je 0 tak se proces generuje ihned

        pid_child = fork();

        if(pid_child == 0) //pokud se fork podaril
        {
            child_proces(log_soub, par, kategorie, i, sd_pam_citac);
        }

        else if(pid_child < 0) // pokud nepodaril tak vypis chybu a ukonci se
        {
            fprintf(stderr, "%s", vypis_chyby[fork_procesu]);
            return -1;
        }

    }


    waitpid(-1, NULL, 0);

    exit(0);
}


int child_proces(FILE *log_soub, parametry *par, int kategorie, int i, int *pam_citac)
{

    int hodnota;

    sem_wait(sem_log_soub); //proces vstupuje a vypisuje starts
        fprintf(log_soub, "%d: %s %d: starts\n", citani(pam_citac, 1), hacker_or_serf[kategorie], i);
    sem_post(sem_log_soub);


    while(*sd_pam_hackers + *sd_pam_serfs == par->c ) // pokud pocet procesu kategorie hackers or serf na molu odpovida kapacite mola
    {
        sem_wait(sem_log_soub);
        fprintf(log_soub, "%d: %s %d: leaves queue : %d: %d \n", citani(pam_citac, 1), hacker_or_serf[kategorie], i, *sd_pam_hackers, *sd_pam_serfs);
        sem_post(sem_log_soub);

        usleep((random() % (par->w))*1000); // uspani na nahodnou dobu z intervalu <20,W>


        sem_wait(sem_log_soub);
        fprintf(log_soub, "%d: %s %d: is back \n", citani(pam_citac, 1), hacker_or_serf[kategorie], i);
        sem_post(sem_log_soub);

    }

    sem_wait(sem_molo); // molo se po pruchodu prvniho procesu na zacatku zamkne

    sem_wait(sem_log_soub);

        if (kategorie == 0) // pokud je aktualni proces hacker tak se na molo prida hacker ,jinak se na molo prida serf
        {
            citani(sd_pam_hackers, 1);
        }
        else
        {
            citani(sd_pam_serfs, 1);
        }
        // Proces vypisuje ze ceka na molu
        fprintf(log_soub, "%d: %s %d: waits : %d: %d \n", citani(pam_citac, 1), hacker_or_serf[kategorie], i, *sd_pam_hackers, *sd_pam_serfs);


    sem_post(sem_log_soub);


    sem_wait(sem_konec); // Prvni proces na zacatku projde, dalsi prochazi do te doby nez se da utvorit posadka

    int kapitan = vyber_posadky(); // fukce zjistujici jestli jde vytvorit posadka



    if(kategorie == 0) // Jakoby zasobnik procesu, kde se procesy rozdeluji do sve kategorie a cekaji na vypusteni
    {
        sem_wait(sem_hacker);
    }

    else
    {
        sem_wait(sem_serf);
    }


    sem_wait(sem_kap_molo); // Pokud byla predchozi plavba skoncena tak projdou 4 procesy



    sem_wait(sem_board); // Po utvoreni posadky (nalezeni kapitana) projdou 4 procesy


    if(kapitan == 0)
    {


        sem_wait(sem_log_soub);
        citani(sd_pam_lod,4); // Pridaji se 4 clenove na lod
        fprintf(log_soub, "%d: %s %d: boards : %d: %d \n", citani(pam_citac, 1), hacker_or_serf[kategorie], i, *sd_pam_hackers, *sd_pam_serfs);
        sem_post(sem_log_soub);

        // Po vstupu 4 procesu na lod se uvolnily 4 mista na molu
        odemceni_semaf(sem_molo, 4);

        usleep((random() % (par->r))*1000); // uspani kapitana na nahodnou dobu z intervalu < 0,R >

        odemceni_semaf(sem_plavba,3); // 3 clenove posadky mohou vystoupit z lodi (kapitan je v teto sekci, posadka je v sekci else)

        sem_wait(sem_pristani); // kapitan ceka dokud nevistoupila posadka

        sem_wait(sem_log_soub);
        citani(sd_pam_lod,-1); // vystupuje kapitan a vypisuje exits
        fprintf(log_soub, "%d: %s %d: captain exits : %d: %d \n", citani(pam_citac, 1), hacker_or_serf[kategorie], i, *sd_pam_hackers, *sd_pam_serfs);
        sem_post(sem_log_soub);

        odemceni_semaf(sem_kap_molo,4); // plavba skoncena takze dalsi 4 procesy mohou na lod

        while(sem_getvalue(sem_konec,&hodnota) != 1)
            odemceni_semaf(sem_konec,1);

    }

    else
    {

        sem_wait(sem_plavba); // clenove posadky cekaji dokud se kapitan nevyspi

        sem_wait(sem_log_soub);
        citani(sd_pam_lod,-1);
        fprintf(log_soub, "%d: %s %d: member exits : %d: %d \n", citani(pam_citac, 1), hacker_or_serf[kategorie], i, *sd_pam_hackers, *sd_pam_serfs);
        sem_post(sem_log_soub);


        if(*sd_pam_lod == 1) // pokud zustal posledni clen na lodi (kapitan) tak muze lod opustit
            sem_post(sem_pristani);

    }


    exit(0);

}

// funkce ktera odemyka semafory
void odemceni_semaf(sem_t *semaf, int kolik)
{
    for(int i = 0; i < kolik; i++)
        sem_post(semaf);
}

// funkce, ktera zjistuje zda jde vybrat posadka
int vyber_posadky(void)
{


    if(*sd_pam_hackers >= 4) // pokud lze vytvorit posadku k plavbe tak odeber prislusny pocet osob z mola, zamkni sem_plavba a pokracuj na plavbu
     {

        citani(sd_pam_hackers,-4); // z mola se odectou 4 hackeri

        odemceni_semaf(sem_board,4); // 4 procesy hacker mohou vstoupit na lod
        odemceni_semaf(sem_hacker,4); // 4 procesy hacker se uvolni ze zasobniku procesu

        return 0;
    }

    else if(*sd_pam_serfs >= 4) // pokud lze vytvorit posadku k plavbe tak odeber prislusny pocet osob z mola  a zamkni sem_plavba a pokracuj na plavbu
    {

        citani(sd_pam_serfs,-4); // z mola se odectou 4 serfove

        odemceni_semaf(sem_board,4); // 4 procesy serfs mohou vstoupit na lod
        odemceni_semaf(sem_serf,4); // 4 procesy serfs se uvolni ze zasobniku procesu

        return 0;

    }

    else if((*sd_pam_serfs >= 2) && (*sd_pam_hackers >= 2)) // pokud lze vytvorit posadku k plavbe tak odeber prislusny pocet osob z mola  a zamkni sem_plavba a pokracuj na plavbu
    {

        citani(sd_pam_serfs,-2); // viz kousek nahore
        citani(sd_pam_hackers,-2);

        odemceni_semaf(sem_board,4);

        odemceni_semaf(sem_serf,2);
        odemceni_semaf(sem_hacker,2);

        return 0;
    }
    else
    {
    // pokud se nepodarila vybrat posadka

    // molo se odemkne pro jeden proces a pak se znovu pokusi vybrat posadka

    sem_post(sem_konec);

    sem_post(sem_molo);

    return 1;
    }


}







// Funkce, ktera pristupuje ke sdilene pameti a pricita nebo odecita hodnotu y

int citani(int *sd_pam, int y)
{
    sem_wait(sem_citac);

    int tmp = 0;


    (*sd_pam) = (*sd_pam) + y;
    tmp = *sd_pam;

    sem_post(sem_citac);

    return tmp;
}





