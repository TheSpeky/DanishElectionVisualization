#%% Take the election dataframe and turn stemmer into percentage for the entire country
def election_result(df):
    mask = df['parti'].str.contains('\.')
    total_votes = df[mask].groupby(['year'])['stemmer'].sum().reset_index()
    total_parti_votes = df[mask].groupby(['parti','year'])['stemmer'].sum().reset_index()
    total_parti_votes['stemmer'] = total_parti_votes.apply(
        lambda row: 
            100 * row['stemmer'] / total_votes.loc[total_votes['year'] == row['year'], 'stemmer'].values[0],
        axis=1
    )
    return total_parti_votes

#%% take the year and return parties with votes
def parties_with_votes(df, year):
    year_df = df[df['year'] == (year)]
    parties_with_votes = year_df[year_df['stemmer'] > 0]
    return parties_with_votes

#%% Color map from party letter to hex color
def party_color(partyLetter):
    color_map = {
        'A' : "#C82518", 
        'B' : "#733280", 
        'C' : "#00571F", 
        'D' : "#00505B", 
        'E' : "#000000", 
        'F' : "#eb94d1", 
        'I' : "#3FB2BE", 
        'K' : "#53619B", 
        'M' : "#B48CD2", 
        "O" : "#FCD03B", 
        'P' : "#0198E1", 
        'Q' : "#E8CCC7", 
        'V' : "#01438E", 
        'Æ' : "#1272C2", 
        'Ø' : "#F7660D", 
        'Å' : "#00FF00"
    }
    return color_map[partyLetter]
