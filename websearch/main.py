from googlesearch import search



class GoogleSearch():
    name = 'google'
    
    def search(self, query):
        search_results = []
        for result in search(query, num_results=4):
            search_results.append(result)

        return search_results



if __name__ == '__main__':
    #testing
    results = GoogleSearch().search('Tennessee Vols Football')
    print(f'''{len(results)} results found''')
    for result in results:
        print(result)


