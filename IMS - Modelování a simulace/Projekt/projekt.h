typedef enum
{
    Empty,
    Susceptible,
    Infected
} State;

typedef struct Cell_data{

    State state;
    uint8_t iters_unchanged = 0; // How many iters was state unchanged. This will be used to calculate how long cells is dead or infected needed for calculate if to kill cell or if to produce an offspring.

} C_data;


typedef struct 
{
    int x_size;         // Amount of cells on X axis
    int y_size;         // Amount of cells on Y xis
    int size;           // Overall amount of cells throughout all axis

    C_data **data;       // Cell data

    float inf_prob;     // Infection propability
    float death_rate;   // Rate of death of infected cells (time after which cell dies)
    float birth_rate;   // Rate of birth into dead cells (time after which cell has a chance to reproduce)

    double infection_density; // Count how many of infected there are per all cells
 
} SpatialDomain;

void init_dom(SpatialDomain *, int x_size, int y_size, float inf_prob, float death_rate, float birth_rate, float inf_density);
int parse_args(int argc, char *argv[], int &dom_size, int &sim_length, bool &visualize, float &inf_prob, float &death_rate, float &birth_rate, float &inf_density);
void print_dom(SpatialDomain *);
double prob_rand_generator();
int update_dom(SpatialDomain *);
int neighbors_count_state(C_data **cells, State state, int x, int y, int x_max, int y_max);

C_data **copy_cells(SpatialDomain *);
void free_cells(C_data **cells, int x_size);

inline int is_infected(SpatialDomain *dom, int x, int y)
{
    if (x < 0 || x >= dom->x_size || y < 0 || y >= dom->y_size)
        return 0;
    return dom->data[x][y].state == Infected;
}

inline int is_susceptible(SpatialDomain *dom, int x, int y)
{
    if (x < 0 || x >= dom->x_size || y < 0 || y >= dom->y_size)
        return 0;
    return dom->data[x][y].state == Susceptible;
}

inline int is_empty(SpatialDomain *dom, int x, int y)
{
    if (x < 0 || x >= dom->x_size || y < 0 || y >= dom->y_size)
        return 0;
    return dom->data[x][y].state == Empty;
}