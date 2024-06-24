import mtg

cards = mtg.find_cards_standard_counter_oracle()
counters = mtg.extract_counters(cards)
filtered_counters = mtg.filter_counters(counters)
mtg.plot_with_plotnine_sorted(filtered_counters, 'Standard: Number of Oracle Text Counter References by Type')
