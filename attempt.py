import os
from googletrans import Translator

translator = Translator()

print(translator.translate('안녕하세요.', dest='en'))

text = 'CASCIANA TERME - APPARTAMENTO rurale centrale completamente da ristrutturare \
    in campagna appena fuori il centro abitatato  bene servito dai mezzi pubblici \
        composto al piano terra da locale stalla con la vecchia mangiatoia  al piano \
            primo dalla cucina ed al piano superiore da due vani con wc. Accessoriato da mq.'

print(translator.translate(text,dest='en'))

