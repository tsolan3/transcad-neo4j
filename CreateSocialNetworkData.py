# from py2neo import Graph, Node, Path, Relationship
#
#
# def connectGraph():
#     graph = Graph("http://localhost:7474/db/data/", user='neo4j', password='119678Qq')
#     return graph
#
#
# def createPeople(self, graph):
#     print("Creating People")
#     bradley = Node('MALE', 'TEACHER', name='Bradley',
#                    surname='Green', age=24, country='US')
#     matthew = Node('MALE', 'STUDENT', name='Matthew',
#                    surname='Cooper', age=36, country='US')
#     lisa = Node('FEMALE', name='Lisa', surname='Adams',
#                 age=15, country='Canada')
#     john = Node('MALE', name='John', surname='Godman',
#                 age=24, country='Mexico')
#     annie = Node('FEMALE', name='Annie', surname='Behr',
#                  age=25, country='Canada')
#     ripley = Node('MALE', name='Ripley',
#                   surname='Aniston', country='US')
#     graph.create(bradley, matthew, lisa, john, annie, ripley)
#     print("People Created")
#     # Create a Dictionary and return back the nodes for
#     people = {'bradley': bradley, 'matthew': matthew, 'lisa': lisa, 'john': john,
#               'annie': annie, 'ripley': ripley}
#     return people
#
#
# def createFriends(self, graph, people):
#         print("Creating Relationships between People")
#         path_1 = Path(people['bradley'], 'FRIEND', people['matthew'], 'FRIEND', people['lisa'], 'FRIEND', people['john'])
#         path_2 = path_1.(people['lisa'], 'FRIEND')
#         path_3 = Path(people['annie'], 'FRIEND', people['ripley'], 'FRIEND', people['lisa'])
#         path_4 = Path(people['bradley'], 'TEACHES', people['matthew'])
#         friendsPath = graph.create(path_2, path_3, path_4)
#         print("Finished Creating Relationships between People")
#         return friendsPath
#
#
# def createMovies(self, graph):
#     print("Creating Movies")
#     firstBlood = Node('MOVIE', name='First Blood')
#     avengers = Node('MOVIE', name='Avengers')
#     matrix = Node('MOVIE', name='matrix')
#     graph.create(firstBlood, avengers, matrix)
#     print("Movies Created")
#     movies = {'firstBlood': firstBlood, 'avengers': avengers, 'matrix': matrix}
#     return movies
#
def rateMovies(self, graph, movies, people):
    print("Start Rating the Movies")
    matthew_firstBlood = Relationship(people['matthew'], 'HAS_RATED', movies['firstBlood'],ratings=4)
    john_firstBlood = Relationship(people['john'], 'HAS_RATED', movies['firstBlood'], ratings=4)
    annie_firstBlood = Relationship(people['annie'], 'HAS_RATED', movies['firstBlood'],ratings=4)
    ripley_firstBlood = Relationship(people['ripley'], 'HAS_RATED', movies['firstBlood'],ratings=4)
    lisa_avengers = Relationship(people['lisa'], 'HAS_RATED', movies['avengers'], ratings=5)
    matthew_avengers = Relationship(people['matthew'], 'HAS_RATED', movies['avengers'],ratings=4)
    annie_avengers = Relationship(people['annie'], 'HAS_RATED', movies['avengers'], ratings=3)
    moviesPath = graph.create(matthew_firstBlood,
                              john_firstBlood,
                              annie_firstBlood,
                              ripley_firstBlood,
                              lisa_avengers,
                              matthew_avengers,
                              annie_avengers)
    print("Finished Rating the Movies")
#     return moviesPath