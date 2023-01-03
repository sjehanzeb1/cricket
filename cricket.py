import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import warnings
from copy import deepcopy, copy
import streamlit as st
import altair as alt
import os, urllib, cv2
import mpld3
import streamlit.components.v1 as components


st.set_page_config(layout="wide")

def main():
   #global number, readme_text
    
    # Render the readme as markdown using st.markdown.
    # if app_mode == st.title('Cricket Network Graph')
    # readme_text = st.markdown(get_file_content_as_string("instructions.md"))
    # content_pub('title','Cricket Network Graphv' )
    # content_pub('message', get_file_content_as_string("instructions.md"))
    # Download external dependencies.
    # for filename in EXTERNAL_DEPENDENCIES.keys():
    #     download_file(filename)

    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    # st.sidebar.image("D:\Online Drives\OneDrive - Institute of Business Administration\MS Data Sciences\Social Networking\cricket\logo.jpg")
    
    # st.sidebar.title("Cricket Analysis \n by \n Syed Jehanzeb", )
    st.sidebar.markdown("""<h1 style='text-align: center;'>
    Cricket Network Graph Analysis <br>
    by <br>
    Syed Jehanzeb</h1>
    <h3 style='text-align: center;'>syed.zeb at gmail.com<br>
    <a style='text-align: center;', href='https://pk.linkedin.com/in/syedzeb'>LinkedIn</a></h3><br>"""
    , unsafe_allow_html=True)
    # st.sidebar.header("by")
    # st.sidebar.header("_Syed Jehanzeb_") 
    # st.sidebar.header("_Syed Jehanzeb_") 
    # st.sidebar.write("_syed.zeb at gmail.com_")
    # st.sidebar.header("[LinkedIn](https://pk.linkedin.com/in/syedzeb)")


    app_mode = st.sidebar.selectbox("Select Tournament",
        ["About", "Pakistan Super League"])#, "Show the source code"])

    if app_mode == "About":
        st.sidebar.success('To continue select a Tournament')
        st.title('Cricket Network Graph')
        st.markdown(get_file_content_as_string("instructions.md"))
    # elif app_mode == "Show the source code":
    #     readme_text.empty()
    #     st.code(get_file_content_as_string("streamlit_app.py"))
    elif app_mode == "Pakistan Super League":
        # team = st.sidebar.selectbox()
        run_the_app()


def run_the_app():
    # To make Streamlit fast, st.cache allows us to reuse computation across runs.
    # In this common pattern, we download data from an endpoint only once.
    # @st.experimental_memo
    @st.cache
    def load_metadata(url):
        # return pd.read_csv(url)
        return pd.read_excel(open(url, 'rb'), sheet_name="Adjacency List Directed")
    number = st.sidebar.slider("Minimum Partnership Runs", 0, 150, 50)
    #loading dataset 
    file ="dataset\PSL Data.xlsx"
    #df = pd.read_excel(open(file, 'rb'), sheet_name="Adjacency List Directed")
    df = load_metadata(file)
    df2 =df 
    df2 = df[df['Repeat']==1]
    df2.loc[:, 'Score'] = df2.loc[:, 'Runs in Partnership']
    pivot = pd.pivot_table(df2, 
            values=['Score', 'Repeat'],
            #values=['Runs in Partnership', 'P1.1', 'P2.1'], 
            index=['P1', 'P2', 'Result', 'Batsman Team'], 
            # columns=['Result'], 
            aggfunc={'Score': np.mean,'Repeat': np.sum},
            fill_value=0)
    df2 = pivot.reset_index()
    df2 = df2.round(0)
    df3 = df2[df2['Score'] > number]
    df3['Score'] = deepcopy(df3['Score'].apply(np.int64))
    df3['Comment'] = "Avg. " + df3['Score'].astype(str) + " in " + df3['Repeat'].astype(str)
    team_name = {
    'IU': 'Islamabad United', 
    'KK': 'Karachi Kings',
    'LQ': 'Lahore Qalandars',
    'MS': 'Multan Sultans',
    'PZ': 'Peshawer Zalmi',
    'QG': 'Quetta Gladiators'      }
    choose_teams(team_name, df3)

    
def choose_teams(teams, df):
    result = st.sidebar.radio("Filter by Match Results", ['Wins', 'Loss', 'Both'], index=2, horizontal=True)
    # print(result)
    if result == 'Wins': 
        df = df[df['Result']==True]
    elif result == 'Loss':
        df = df[df['Result']==False]
    
    checkbox_team = st.sidebar.checkbox("Team Selection")
    team_select = st.sidebar.selectbox("Please select team",  tuple(teams.values()) , disabled=not checkbox_team)
    if checkbox_team:
        # team_select = st.sidebar.selectbox("Please select team",  tuple(teams.values()) )
        team_swap = {v: k for k, v in teams.items()}
        df = df[df['Batsman Team']==team_swap.get(team_select)]
    else: team_select = "All Teams"
    cb1 = st.sidebar.checkbox("Players Selection")
    # if cb1: player_select = st.sidebar.selectbox("Please select Player", pd.unique(df[['P1', 'P2']].values.ravel('K')))
    # if cb1: df = df[(df['P1']==player_select) | (df['P2']==player_select)]
    player_select = st.sidebar.selectbox("Please select Player", pd.unique(df[['P1', 'P2']].values.ravel('K')), disabled=not cb1)
    if cb1: df = df[(df['P1']==player_select) | (df['P2']==player_select)]    

    G = nx.from_pandas_edgelist(df, "P1", "P2", True)
    # readme_text = ""
    # main.__name__.tit
    # if team_select == "": team_select = "All Teams"
    # content_pub('message', team_select)
    make_graph(G, team_select)
    wins, loss = make_results(df)
    left, right = st.columns(2)
    with left: 
        st.header("Winning Partnerships")
        st.dataframe(wins)
    with right:
        st.header("Lossing Partnerships")
        st.dataframe(loss)



def make_graph(G, title1):
    plt.rcParams["figure.figsize"] = (10,9)
    linewin = [(u, v) for (u, v, d) in G.edges(data=True) if d["Result"] == True]
    lineloss = [(u, v) for (u, v, d) in G.edges(data=True) if d["Result"] == False]
    edges = G.edges(data=True)
    linesizeloss = [d['Repeat'] for (u, v, d) in edges if d["Result"] == False]
    linesizewin = [d['Repeat'] for (u, v, d) in edges if d["Result"] == True]


    pos =   nx.circular_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=200)
    nx.draw_networkx_edges(G, pos, edgelist=linewin, width=linesizewin)
    nx.draw_networkx_edges(
        G, pos, edgelist=lineloss, width=linesizeloss,  alpha=0.5, edge_color="r", style="dashed"
    )
    # node labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(G, "Comment")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)
    
    ax = plt.gca()
    fig = plt.gcf()
    # ax.set_title("Influential Partnerships at " + title1,fontdict={'fontsize': 37.5})
    
    # st.markdown("Influential Partnerships at " + title1)
    content_pub("title", "Influential Partnerships for " + title1)
    ax.margins(0.08)
    # print(type(title1))
    # plt.savefig("images\\" + title1 + ".png")
    plt.axis("off")
    plt.tight_layout()
    # plt.show()
    fig_html = mpld3.fig_to_html(fig)
    components.html(fig_html, height=1000)
    # st.pyplot(fig)



@st.experimental_singleton(show_spinner=False)
def get_file_content_as_string(path):
    #url = 'http://localhost:8501/' + path
    url = 'D:\\Online Drives\\OneDrive - Institute of Business Administration\\MS Data Sciences\Social Networking\\' + path
    myfile = open(url)
    return_response = myfile.read()
    # print(url)
    #response = urllib.request.urlopen(url)
    # return_response  = response.read().decode("utf-8")
    return return_response


def content_pub(type, content):
    if type.lower() == 'title': title = st.title (content)
    if type.lower() == 'message': message = st.markdown(content)

# title = st.title('Cricket Network Graph')
# readme_text = st.markdown(get_file_content_as_string("instructions.md"))

# pages 
def make_results(df):
    for result in True, False:
        df_g = df[df['Result']==result]
        G2 = nx.from_pandas_edgelist (df_g, "P1", "P2", True)
        d = pd.DataFrame(G2.degree(weight='Repeat'))
        r = pd.DataFrame()
        if d.shape[1] >= 2: 
            d.columns =['Player', 'Degree'] 
            d['Rank']  = d['Degree'].rank(ascending = False, method='min').astype(int)
            r = d[['Rank', 'Player', 'Degree']].sort_values(by=['Rank'])
        if result == True: wins = r
        if result == False: loss = r
    return wins, loss



if __name__ == "__main__":
    main()