from googlesearch import search



class GoogleSearch():
    name = 'google'
    
    def search(self, query, message):
        search_results = []
        for result in search(query, num_results=5):
            search_results.append(result)
        return search_results
