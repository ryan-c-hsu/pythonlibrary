""" Silly crude data parser for a guy on Discord

Note that this will fail if one field name is "nested" inside another,
e.g. "Payment" and "Payment Info" cannot both be field names, but
"Blue Bird Song" and "Red Bird Beak" are okay
"""
import logging

logger = logging.getLogger()

keywords = ['WIRE TYPE', 'IN DATE', 'TIME', 'TRN', 'SEQ', 'ORIG', 'FX', 'ORIG BK', 'ID', 'SND BK', 'ID', 'PMT DET', 'DES', 'ID', 'INDN','SNDR REF','BNF BK','BNF','SERVICE REF']
keywords_tokenized = [keyword.upper().split() for keyword in keywords]
    

def parse(text):
    text = text.replace(':', ' : ')  # make sure there's whitespace around ':'s which are important
    words = text.upper().split()

    result = {}
    current_data_tokens = []
    current_field_tokens = []
    is_field_tokens = False
    id_flag = False
    id_info = None
    id_field = None
    
    logger.debug(len(words))
    
    for i, word in enumerate(reversed(words)):
        
        logger.debug(f'{i}:{word}')
        
        if word == ':':
            is_field_tokens = True
            continue

        if is_field_tokens:
            current_field_tokens.insert(0, word)
            if current_field_tokens in keywords_tokenized:
                if ' '.join(current_field_tokens) == 'ID':
                    id_flag = True
                    id_info = ' '.join(current_data_tokens)
                    
                    current_data_tokens = []
                    current_field_tokens = []
                    is_field_tokens = False
                    
                elif id_flag == True:
                    id_field = ' '.join(current_field_tokens) + " ID"
                    result[id_field] = id_info
                    logger.debug(f'{id_field} : {id_info}')
                    
                    current_fieldname = ' '.join(current_field_tokens)
                    current_data = ' '.join(current_data_tokens)
                    result[current_fieldname] = current_data
                    logger.debug(f'{current_fieldname} : {current_data}')
                    
                    # And now reset everything.
                    id_flag = False
                    id_info = None
                    id_field = None
                    current_data_tokens = []
                    current_field_tokens = []
                    is_field_tokens = False
                    
                else:
                    # We did it! We found a complete field name.
                    # Now add it to the result.
                    current_fieldname = ' '.join(current_field_tokens)
                    current_data = ' '.join(current_data_tokens)
                    result[current_fieldname] = current_data
                    logger.debug(f'{current_fieldname} : {current_data}')
                    
                    # And now reset everything.
                    current_data_tokens = []
                    current_field_tokens = []
                    is_field_tokens = False
        else:
            if i == len(words)-1:
                current_fieldname = 'Company'
                current_data_tokens.insert(0, word)
                current_data = ' '.join(current_data_tokens)
                result[current_fieldname] = current_data
                current_data_tokens = []
                current_field_tokens = []
            else:
                current_data_tokens.insert(0, word)


    return result


def test():
    logging.basicConfig(level=logging.DEBUG)

    text = 'WIRE TYPE:WIRE OUT DATE:190208 TIME:1404 ET TRN:2019020800312017 SERVICE REF:339728 BNF:PREVIOUS DAY RETURN ID:CH302333 BNF BK:CITIBAN K, N.A. ID:0008 PMT DET:BOA2776-06FEB19 /ACC/RTN Y R SSN 0386690 DTD 20-NOV//-18 FOR 22,500.00/USD RT'
    expected = {
        'BANK': 'CHASE',
        'PAYMENT INFO': '100AB',
        'AMOUNT': '100'
    }
    
    
    logger.debug(text)
    
    data = parse(text)
    
    for fields in data:
        print(fields + ":" + data[fields])
    
    print('It works!!')


if __name__ == '__main__':
    test()
