import os
from googletrans import Translator

translator = Translator()

print(translator.translate('안녕하세요.', dest='en'))

text = 'Casa rustica terratetto da ristrutturare sempre soleggiata , con possibilità di \
    ampliamento del 30%, libera su n.3 lati con ampio terreno e area boscata.'

print(translator.translate(text,dest='da'))

