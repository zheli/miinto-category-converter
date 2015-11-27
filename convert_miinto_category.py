#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import re

from bs4 import BeautifulSoup

CSV_COL_SEP=';'

def _get_category_dict(bs_element, parent_category=None):
    miinto_pattern = r'\((\d+)\)\s([\S\s]+)'
    result = re.compile(miinto_pattern).match(bs_element.text.strip())
    if parent_category:
        category = '%s > %s' % (parent_category['category'], result.group(2))
    else:
        category = result.group(2)
    return {'id': result.group(1), 'category': category}


def _convert_category_to_string(category):
    return u'{id}{separator}{category}\n'.format(separator=CSV_COL_SEP, **category).encode('utf-8')


def main(filename):
    counter = 0
    with open(filename) as input_file, \
            open(os.path.splitext(filename)[0]+'.csv', 'w') as output_file:
        soup = BeautifulSoup(input_file, 'lxml')
        for table in soup.findAll('table'):
            trs = table.findAll('tr')

            h3_category = _get_category_dict(trs[0].find('h3'))
            print(_convert_category_to_string(h3_category))
            output_file.write(_convert_category_to_string(h3_category))
            counter += 1

            new_main_category = {}
            for tr in trs[2:]:
                [main_category, child_category] = tr.findAll('td')

                if main_category and main_category.text:
                    new_main_category = _get_category_dict(main_category,
                                                           parent_category=h3_category)
                    print(_convert_category_to_string(new_main_category))
                    output_file.write(_convert_category_to_string(new_main_category))
                    counter += 1

                if child_category and child_category.text:
                    child_category = _get_category_dict(child_category,
                                                        parent_category=new_main_category)
                    print(_convert_category_to_string(child_category))
                    output_file.write(_convert_category_to_string(child_category))
                    counter += 1

    print('Found %d categories' % counter)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Miinto html category file to csv')
    parser.add_argument('--file', action='store', dest='filename', help='Miinto category file')
    arguments = parser.parse_args()
    if arguments.filename:
        main(arguments.filename)
    else:
        parser.print_help()
