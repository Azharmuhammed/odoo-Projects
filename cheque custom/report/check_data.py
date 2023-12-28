from odoo import api, fields, models, _
from datetime import date


to_19 = ('Zero',  'One',   'Two',  'Three', 'Four',   'Five',   'Six',
                   'Seven', 'Eight', 'Nine', 'Ten',   'Eleven', 'Twelve', 'Thirteen',
                   'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen')
tens  = ('Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety')
denom = ('', 'Thousand', '')


class check_data_get(models.Model):
    _inherit = "account.payment"

    def check_data_get(self):
        '''Function for splitting check date'''
        for rec in self:
            date_dict = {}
            payment_date = str(rec.date)
            count = 0
            today = payment_date.split('-')
            for d in today:
                if len(d) == 2:
                    count = count + 1
                    date_dict.update({count:d[0]})
                    count = count + 1
                    date_dict.update({count:d[1]})
                elif len(d) == 4:
                    count = count + 1
                    date_dict.update({count:d[0]})
                    count = count + 1
                    date_dict.update({count:d[1]})
                    count = count + 1
                    date_dict.update({count:d[2]})
                    count = count + 1
                    date_dict.update({count:d[3]})
            return date_dict

    def amount_to_text_wrapp(self, amt, obj):
        amt_text = []
        amount_text = self.amount_to_text(amt, obj)
        position_list = [pos for pos, char in enumerate(amount_text) if char == ' ']
        if len(amount_text) > 26:
            if amount_text[26] not in ('-', ' '):
                txt_pos = [p for p in position_list if p < 39][-1]
                amt_text.append((amount_text[0:txt_pos],amount_text[txt_pos:-1],amount_text[-1]))
            else:
                amt_text.append((amount_text[0:26],amount_text[26:-1],amount_text[-1]))
        return amt_text
                
                
    
    def _convert_nn(self, val):
        """convert a value < 100 to English.
        """
        if val < 20:
            return to_19[val]
        for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
            if dval + 10 > val:
                if val % 10:
                    return dcap + '-' + to_19[val % 10]
                return dcap

    def _convert_nnn(self, val):
        """
            convert a value < 1000 to english, special cased because it is the level that kicks
            off the < 100 special case.  The rest are more general.  This also allows you to
            get strings in the form of 'forty-five hundred' if called directly.
        """
        word = ''
        (mod, rem) = (val % 100, val // 100)
        if rem > 0:
            word = to_19[rem] + ' Hundred'
            if mod > 0:
                word += ' '
        if mod > 0:
            word += self._convert_nn(mod)
        return word

    def english_number(self, val):
        ''' This function returns engish number '''
        if val < 100:
            return self._convert_nn(val)
        if val < 1000:
             return self._convert_nnn(val)
        for (didx, dval) in ((v - 1, 100 ** v) for v in range(len(denom))):
            dval = dval * 10
            if dval > val:
                mod = (100 ** didx) * 10
                l = val // mod
                r = val - (l * mod)
                ret = self._convert_nn(l) + ' ' + denom[didx]
                if r > 0:
                    ret = ret +' '+ self.english_number(r)
                return ret

    def amount_to_text(self, number, object):
        ''' This function returns amount to text '''
        number = '%.3f' % number
        units_name = object.currency_id.name
        list = str(number).split('.')
        start_word = self.english_number(int(list[0]))
        end_word = self.english_number(int(list[1]))
        end_word = str(int(list[1]))
        fils_number = int(list[1])
        fils_name = (fils_number > 1) and 'Paisa' or 'Ps'
        word = 'Only'
        word1 = 'Fils Only'
        if end_word == '0' and fils_number == 0:
            fils_name = ' '
            end_word = ' '
            return ' '.join(filter(None, [start_word, (start_word) and (end_word) and  end_word, word]))
        else:
            return ' '.join(filter(None, [start_word, (start_word) and (end_word) and 'and', end_word, word1]))
    
    def _get_amount(self):
        return str("{:0,.3f}".format(self.amount))
