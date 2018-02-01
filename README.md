# March Madness Prediction

I wrote script to scrape data from https://www.sports-reference.com/cbb/ data for the past 5 tournaments (2010 to 2016) to generate an algorithm to predict the 2017 tournament.

My algorithm is relatively simple: for each team, I extracted 30 team stats based on their regular season performace, weighed those stats with respective to other teams in the tournament. Then I generate a population of vectors that includes 30 randomly generated number. Each algorithm gives a weight to each of the team's stats and the prediction of a head to head matchup is dependant on the dot product of the team stats with the vector. It's a basic application of genetic algorithm: where you generate a population of randomly generated vectors, and pick the "fittest" vectors and passed on to the next generation.

Ultimately, this might not be the best approach, since in the training data, its' accuracy is only around 62%.

In the future, I plan to use ML or Tensored Flow for better predictive power.
