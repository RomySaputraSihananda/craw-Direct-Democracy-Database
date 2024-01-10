import os

from pyquery import PyQuery
from requests import Session, Response

from concurrent.futures import ThreadPoolExecutor

from democracy.helpers import Parser, counter_time, logging

class Democracy:
    def __init__(self) -> None:
        self.__parser: Parser = Parser()
        self.__requests: Session = Session()
        self.__BASE_URL: str = 'https://www.idea.int'

    def __download(self, file_name: str, url):
        response: Response = self.__requests.get(url)

        if(not os.path.exists('data')):
                os.makedirs('data')
                
        with open(f'data/{file_name}.xlsx', 'wb') as file:
            file.write(response.content)
        
        logging.info(f'success download data/{file_name}.xlsx')

    def __get_database(self, quetion: dict) -> None:
        quetion, quetion_id = list(quetion.items())[0]
        
        self.__download(quetion, f'https://www.idea.int/data-tools/export?type=region_and_question&themeId=309&questionId={quetion_id}&world=')

    @counter_time
    def execute(self):
        response: Response = self.__requests.get('https://www.idea.int/data-tools/data/direct-democracy-database')

        quetions: list = [{PyQuery(option).text().lower().replace(' ', '_').replace('/', '_'): PyQuery(option).attr('value')} for option in self.__parser.execute(response.text, '#database-question .level1')]
        
        self.__download('all_data', self.__BASE_URL + self.__parser.execute(response.text, '#block-tema-content .btn.btn-s--pill.btn-c--hollow').attr('href'))

        with ThreadPoolExecutor() as executor:
            executor.map(self.__get_database, quetions)
        executor.shutdown(wait=True)


if(__name__ == '__main__'):
    democracy: Democracy = Democracy()
    democracy.execute()