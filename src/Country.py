from data import *


class Country:
    """
    The class object representing a country and its relative information about the number of suspected, infected and
    recovered individuals in the population for each time step t between 0 and H.
    """
    def __init__(self, name="Country", H=horizon, N=1000, beta=0.2, gamma=1. / 10, I0=0, R0=0):
        """
        Construction method
        :param name: name of the country
        :param H: the range of time period in terms of days for the simulation
        :param N: total population in the country
        :param beta: contract rate of the virus
        :param gamma: recovery rate of the virus
        :param I0: number of infected individuals in the country at time step 0
        :param R0: number of recovered individuals in the country at time step 0
        """
        self.name = name
        # Horizon
        self.H = H
        # Total population, N.
        self.N = N
        # Initial number of infected and recovered individuals, I0 and R0.
        self.I0, self.R0 = I0, R0
        # Everyone else, S0, is susceptible to infection initially.
        self.S0 = self.N - self.I0 - self.R0
        # Contact rate, beta, and mean recovery rate, gamma, (in 1/days).

        self.gamma = gamma
        self.beta = [beta for t in range(H)]
        self.S = [0.0 for t in range(H)]
        self.I = [0.0 for t in range(H)]
        self.R = [0.0 for t in range(H)]
        self.S[0] = self.S0
        self.I[0] = self.I0
        self.R[0] = self.R0

    def simulate(self, t):
        """
        Method simulating the spread of a virus inside a country following a classic SIR model on time step t.
        :param t: the time step on which the evolution of the virus is to be simulated
        """
        dS = -self.beta[t] * self.S[t - 1] * self.I[t - 1] / self.N
        dI = self.beta[t] * self.S[t - 1] * self.I[t - 1] / self.N - self.gamma * self.I[t - 1]
        dR = self.gamma * self.I[t - 1]
        self.S[t] = self.S[t - 1] + dS
        self.I[t] = self.I[t - 1] + dI
        self.R[t] = self.R[t - 1] + dR


def migration(t, countries, mig):
    """
    Method simulating the exchanges of population due to the migration between the different countries at time step t.
    The ratios of suspected, infected and recovered individuals moving are proportional to the actual ratio of
     suspected, infected and recovered individuals in the population of the origin country.
    :param t: the time step on which the migrations between countries are to be applied
    :param countries: the list of Country objects representing the different countries on which the migrations are applied
    :param mig: the migration matrix containing the number of daily movers between each pair of country for each time step
    """
    n = len(countries)
    pop = np.array([c.N for c in countries])

    prop = [[mig[t][i][j] / pop[i] for j in range(n)] for i in range(n)]

    S = [c.S[t] for c in countries]
    I = [c.I[t] for c in countries]
    R = [c.R[t] for c in countries]
    for i in range(n):
        countries[i].S[t] = S[i]
        countries[i].I[t] = I[i]
        countries[i].R[t] = R[i]
        for j in range(n):
            countries[i].S[t] -= prop[i][j] * S[i]  # out migration
            countries[i].S[t] += prop[j][i] * S[j]  # in migratiuon
            countries[i].I[t] -= prop[i][j] * I[i]  # out migration
            countries[i].I[t] += prop[j][i] * I[j]  # in migratiuon
            countries[i].R[t] -= prop[i][j] * R[i]  # out migration
            countries[i].R[t] += prop[j][i] * R[j]  # in migration


def simulate(countries, mig, Horizon=horizon):
    """
    Method simulating the spread of a virus in an ensemble of countries following a Multi-Country SIR model.
    :param countries: the list of Country objects representing the different countries on which the migrations are applied
    :param mig: the migration matrix containing the number of daily movers between each pair of country for each time step
    :param Horizon: the range period in terms of days for the simulation
    :return: a list of the evolution of infected individuals in each country for every time step t
    """
    for t in range(1, Horizon):
        for c in countries:
            c.simulate(t)
        migration(t, countries, mig)
    return [c.I.copy() for c in countries]



def create_countries(name_countries,origin='united kingdom',beta=0.2,gamma=0.1,I0=10,Horizon=horizon):
    """
    Function creating a list of Country object
    :param name_countries: list of the names of each country
    :param origin:  country of origin of the virus
    :param beta: value of the contract rate of the virus for every country
    :param gamma: value of the recovery rate of the virus for every country
    :param I0: number of infected individuals in the origin country of the virus at time step 0
    :param Horizon: the range period in terms of days for the simulation
    :return: a list of Country object representing each country in the name_countries list
    """
    countries = []
    for country in name_countries:
        if country == origin:
            c = Country(name=country,N=df_countries['population'].loc[country],beta=beta,gamma=gamma,I0=I0,H=Horizon)
        else:
            c = Country(name=country,N=df_countries['population'].loc[country],beta=beta,gamma=gamma,I0=0,H=Horizon)
        countries.append(c)
    return countries


def modify_mig(country1,country2,countries,factor,mig,t=0):
    """
    Function modifying the value of daily movers between 2 countries for the period of time [t,Horizon]
    :param country1: the first country of the pair of countries with the whose the migration flux will be modified
    :param country2: the second country of the pair of countries with the whose the migration flux will be modified
    :param countries: the list of Country object
    :param factor: the factor by which the number of daily movers will be multiply
    :param mig: the migration matrix containing the number of daily movers between each pair of country for each time step
    :param t: the time step from which he numbers of daily movers between the 2 countries will be modified
    :return: the modified migration matrix containing the number of daily movers between each pair of country for each time step
    """
    if (country1 in countries or country1 == 'all') and (country2 in countries or country2 == 'all') :
        if (type(factor) == int or type(factor) == float or factor.replace('.','',1).isdigit()) and float(factor) >=0.0:
            if (type(t) == int or t.isdigit()) and int(t) >= 0:
                t = int(t)
                factor = float(factor)
                if country1 == 'all':
                    country1 = range(len(countries))
                else:
                    country1 = [countries.index(country1)]
                if country2 == 'all':
                    country2 = range(len(countries))
                else:
                    country2 = [countries.index(country2)]
                for i in country1:
                    for j in country2:
                        mig[t:,i,j] = mig[t,i,j] * factor
                        mig[t:,j,i] = mig[t,j,i] * factor
    return mig






