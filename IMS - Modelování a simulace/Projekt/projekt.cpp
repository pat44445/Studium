#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <math.h>
#include <unistd.h>

#include <iostream>
#include <fstream>
#include "projekt.h"

// Default input variables for the model
#define DEF_DOM_SIZE 50
#define DEF_INF_PROB 0.1
#define DEF_DEATH_RATE 0.5
#define DEF_BIRTH_DATE 0.5
#define DEF_INF_DENS 0.1
#define DEF_SIM_LENGTH 100

using namespace std;

int main(int argc, char *argv[])
{
    bool visualize;
    float inf_prob, death_rate , birth_rate, inf_density;
    int dom_size, sim_length, ret;
    
    SpatialDomain dom;

    ret = parse_args(argc, argv, dom_size, sim_length, visualize, inf_prob, death_rate, birth_rate, inf_density);
    if (ret)
        return ret == 1 ? 0 : 1; // If parser returned 1 exit program with zero otherwise exit program with 1 

    init_dom(&dom, dom_size, dom_size, inf_prob, death_rate, birth_rate, inf_density);

    ofstream f;
    f.open("data.dat");

    for (int i = 0; i < sim_length; i++) {
        if (visualize) {
            print_dom(&dom);
            usleep(500000);
        }
        f << i << "\t" << dom.infection_density << endl;

        ret = update_dom(&dom);
        if (ret) {
            fprintf(stderr, "Internal error\n");
            return 1;
        }
    }

    f.close();
}

// Generate values between 0 and 1 in uniform distribution
double prob_rand_generator()
{
    uint32_t ix = rand();
    ix = ix * 69069u + 1u;
    return ix / ((double)UINT32_MAX + 1.0);
}

// Count neighbors matching desired state in Moore neighborhood
int neighbors_count_state(C_data **cells, State state, int x, int y, int x_max, int y_max)
{
    int count = 0;

    // Matrices are used in for loop to get neighbor coordinates for Moore neighborhood from a increment 
    const int8_t x_neigh_matrix[] = {-1, 0, 1, -1, 1, -1, 0, 1};
    const int8_t y_neigh_matrix[] = {-1, -1, 1, 0, 0, 1, 1, 1};
    const uint8_t neighbors_c = 8;

    for (int i = 0; i < neighbors_c; i++) {
        int nx = x + x_neigh_matrix[i];
        int ny = y + y_neigh_matrix[i];

        if (nx < 0 || ny < 0 || nx >= x_max || ny >= y_max)
            continue;

        if (cells[nx][ny].state == state)
            count++;
    }
    return count;
}

// Update spatial domain as infect, death, birth procedures
int update_dom(SpatialDomain *dom)
{
    double probability;
    int count;

    int infected = 0; // Count how many infected there are in this iteration

    C_data **orig_cells = copy_cells(dom);

    for (int x = 0; x < dom->x_size; x++) {
        for (int y = 0; y < dom->y_size; y++) {

            const C_data *orig_cell = &orig_cells[x][y];
            C_data *cell = &dom->data[x][y];

            switch (orig_cell->state) {
                case Empty:
                    // If orig_cell is empty birth can happen
                    if (orig_cell->iters_unchanged * dom->birth_rate >= 1.0) {
                        // Cell must be empty long enough to have a chance to produce offspring
                        count = neighbors_count_state(orig_cells, Susceptible, x, y, dom->x_size, dom->y_size); // Count susceptible neighbors
                        probability = 1 - pow(1 - dom->birth_rate, count);

                        if (prob_rand_generator() < probability) {
                            cell->state = Susceptible;
                            cell->iters_unchanged = 0;
                        }
                    }
                    break;
                case Susceptible:
                    // If orig_cell is susceptible it can get infected
                    count = neighbors_count_state(orig_cells, Infected, x, y, dom->x_size, dom->y_size); // Count infected neighbors
                    probability = 1 - pow(1 - dom->inf_prob, count);

                    if (prob_rand_generator() < probability) {
                        cell->state = Infected;
                        cell->iters_unchanged = 0;
                        infected++;
                    }
                    break;
                case Infected:
                    // If orig_cell is infected it dies after given time
                    if (prob_rand_generator() < dom->data[x][y].iters_unchanged * dom->death_rate) {
                        // Infected orig_cell must be infected for long enough to have a chance to die
                        dom->data[x][y].state = Empty;
                        dom->data[x][y].iters_unchanged = 0;
                    }
                    infected++;
                    break;
                default:
                    return 1;
            }
        cell->iters_unchanged++;
        }
    }
    free_cells(orig_cells, dom->x_size);
    dom->infection_density = (double)infected / dom->size;
    return 0;
}

// Make a copy of spatial domain
C_data **copy_cells(SpatialDomain *dom) {
    C_data **cells = (C_data **)malloc(dom->x_size * sizeof(*dom->data));

    for(int x = 0; x < dom->x_size; x++) {
        cells[x] = (C_data *)malloc(dom->y_size * sizeof(**dom->data));

        for (int y = 0; y < dom->y_size; y++) {
            cells[x][y].state = dom->data[x][y].state;
            cells[x][y].iters_unchanged = dom->data[x][y].iters_unchanged;
        }
    }
    return cells;
}

// Free all cells of spatial domain
void free_cells(C_data **cells, int x_size) {
    for(int x = 0; x < x_size; x++)
        free(cells[x]);
    free(cells);
}

// Initialize spatial domain
void init_dom(SpatialDomain *dom, int x_size, int y_size, float inf_prob, float death_rate, float birth_rate, float inf_density)
{
    int infected;

    dom->x_size = x_size;
    dom->y_size = y_size;
    dom->size = x_size * y_size;

    dom->inf_prob = inf_prob;
    dom->death_rate = death_rate;
    dom->birth_rate = birth_rate;
    dom->infection_density = inf_density;

    dom->data = (C_data **)malloc(x_size * sizeof(*dom->data));

    for(int x = 0; x < x_size; x++) {
        dom->data[x] = (C_data *)malloc(y_size * sizeof(**dom->data));

        for (int y = 0; y < y_size; y++) {
            dom->data[x][y].state = Susceptible;
        }
    }

    infected = dom->size * inf_density;

    srand(time(NULL));

    for (int i = 0; i < infected; i++) {
        int x,y;
        do {
            x = rand() % x_size;
            y = rand() % y_size;
        }
        while (is_infected(dom, x, y));
        dom->data[x][y].state = Infected;
        dom->data[x][y].iters_unchanged = 0;
    }
}

// Print spatial domain
void print_dom(SpatialDomain *dom)
{
    system("clear");

    for (int x = 0; x < dom->x_size; x++) {
        for (int y = 0; y < dom->y_size; y++) {
            if (dom->data[x][y].state == Susceptible)
                printf("- ");
            else if (dom->data[x][y].state == Infected)
                printf("X ");
            else
                printf("  ");
        }
        printf("\n");
    }
}

// Parse arguments
int parse_args(int argc, char *argv[], int &dom_size, int &sim_length, bool &visualize, float &inf_prob, float &death_rate, float &birth_rate, float &inf_density)
{
    int opt;

    // Default values that can be overwritten by args
    visualize = false;
    inf_prob = DEF_INF_PROB;
    death_rate = DEF_DEATH_RATE;
    birth_rate = DEF_BIRTH_DATE;
    inf_density = DEF_INF_DENS;
    dom_size = DEF_DOM_SIZE;
    sim_length = DEF_SIM_LENGTH;

    while((opt = getopt(argc, argv, "hvi:d:b:I:s:l:")) != -1) {
        switch (opt) {
            case 'v':
                visualize = true;
                break;
            case 'i':
                inf_prob = strtof(optarg, NULL);
                break;
            case 'd':
                death_rate = strtof(optarg, NULL);
                break;
            case 'b':
                birth_rate = strtof(optarg, NULL);
                break;
            case 'I':
                inf_density = strtof(optarg, NULL);
                break;
            case 's':
                dom_size = strtol(optarg, NULL, 10);
                break;
            case 'l':
                sim_length = strtol(optarg, NULL, 10);
                break;
            case 'h':
                printf("Cellular automata based epidemic spread model. Results are written into data.dat file.\n");
                printf("Usage:\n");
                printf("\t ./proj [options]\n\n");
                printf("Options:\n");
                printf("-h\t\t Print this message\n");
                printf("-v\t\t Print current state of cellular automata into standard output after each new iteration\n");
                printf("-i INFECT_PROB\t Infection probabilty after which susceptible cells can become infected\n");
                printf("-d DEATH_RATE\t Death rate after which infected cells die and become empty\n");
                printf("-b BIRTH_RATE\t Birth rate after which empty cell can produce offspring from neighboring susceptible cells\n");
                printf("-I INFECT_DENS\t Infected density used for generate infected cells for initialisation at time 0\n");
                printf("-s SIZE\t\t Size how many cells spatial domain is wide and high\n");
                printf("-l TIME\t\t How many iterations should simulation run\n");
                return 1;
        }
    }

    if (visualize && dom_size > 150) {
        fprintf(stderr, "Cannot visualize more than width 150 cells\n");
        return 2;
    }

    // printf ("visualize %s\n", visualize ? "true" : "false");
    // printf ("inf_prob %f\n", inf_prob);
    // printf ("death_rate %f\n", death_rate);
    // printf ("birth_rate %f\n", birth_rate);
    // printf ("inf_density %f\n", inf_density);
    // printf ("dom_size %d\n", dom_size);

    return 0;
}