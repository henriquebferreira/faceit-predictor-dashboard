VALID_MAP_NAMES = ["dust2", "mirage", "inferno", "nuke", "train", "ancient", "vertigo", "cache", "overpass"]

def get_prediction_bar(map_name, prob_A, prob_B):
    if map_name not in VALID_MAP_NAMES:
        image_element = f'<div class="fp-map-image"></div>'
    else:
        image_element = f'<img class="fp-map-image" src="https://cdn.faceit.com/static/stats_assets/csgo/maps/110x55/csgo-votable-maps-de_{map_name}-110x55.jpg"></img>'
    bar_html = """
                <div class="fp-prediction">
                     <div class="fp-prediction-info">
                        IMAGE_ELEMENT
                        <span class="fp-map-name">MAP_NAME</span>
                    </div>
                    <div class="fp-weighted-bar">
                        <div class="fp-weighted-teambar TEAM_BAR_A" style="flex-basis: PROB_A%">
                            PROB_A%
                        </div>
                        <div class="fp-weighted-teambar TEAM_BAR_B" style="flex-grow: 1">
                            PROB_B%
                        </div>
                    </div>
                </div>
                """
    bar_html = bar_html.replace("PROB_A",  prob_A)
    bar_html = bar_html.replace("PROB_B",  prob_B)
    bar_html = bar_html.replace("IMAGE_ELEMENT",  image_element)
    bar_html = bar_html.replace("MAP_NAME",  map_name)
    try: 
        if float(prob_A) >= float(prob_B):
            team_bar_a, team_bar_b = 'fp-background-gt', 'fp-background-lt'
        else:
            team_bar_a, team_bar_b = 'fp-background-lt', 'fp-background-gt'
        bar_html = bar_html.replace("TEAM_BAR_A", team_bar_a)
        bar_html = bar_html.replace("TEAM_BAR_B", team_bar_b)
    except:
        bar_html = bar_html.replace("TEAM_BAR_A", 'fp-background-gt')
        bar_html = bar_html.replace("TEAM_BAR_B", 'fp-background-lt')

    return bar_html