class AnalysisAgent:
    def find_fvg_bisi(data, remove_rebalanced=True):
        bisi = []
        for i in range(len(data)):
            if i == 0 or i == len(data)-1:
                continue
            else:
                if data[i-1]['high'] < data[i+1]['low']:
                    bisi.append({'low': data[i-1]['high'], 'high': data[i+1]['low'], 'datetime': data[i]['datetime']})
        if not remove_rebalanced:
            return bisi
        else:
            unpurged_bisi = []
            for fvg in bisi:
                purged = False
                for candle in data:
                    if candle['datetime'] > fvg['datetime']:
                        if candle['low'] < fvg['low']:
                            purged = True
                    if not purged:
                        unpurged_bisi.append(fvg)
            return unpurged_bisi

    def find_fvg_sibi(data):
        sibi = []
        for i in range(len(data)):
            if i == 0 or i == len(data)-1:
                continue
            else:
                if data[i-1]['low'] > data[i+1]['high']:
                    sibi.append({'low': data[i+1]['high'], 'high': data[i-1]['low']})
        if not remove_rebalanced:
            return sibi
        else:
            unpurged_sibi = []
            for fvg in sibi:
                purged = False
                for candle in data:
                    if candle['datetime'] > fvg['datetime']:
                        if candle['high'] > fvg['high']:
                            purged = True
                        if not purged:
                            unpurged_sibi.append(fvg)
            return unpurged_sibi

    def find_sellside_liquidity(self, data, num_neighbours=1):

        def check_neighbours_for_low(current_low, data, i, num_neighbours):
            for j in range(1,num_neighbours+1):
                if not (current_low<data[i-j]['low'] and current_low<data[i+j]['low']):
                    return False
            return True

        liquidities = []
        for i in range(len(data)):
            current_low = data[i]['low']
            if (i<num_neighbours or i>len(data)-num_neighbours-1):
                continue
            else:
                if check_neighbours_for_low(current_low, data, i, num_neighbours):
                    liquidities.append({'datetime':data[i]['datetime'], 'price': data[i]['low']})

        filtered_liquidities = []
        for liquidity in liquidities:
            liquidity_purged = False
            for i in data:
                if i['datetime'] > liquidity['datetime']:
                    if i['low']< liquidity['price']:
                        liquidity_purged = True
                        break
            if not (liquidity_purged):
                filtered_liquidities.append(liquidity)

        return filtered_liquidities
        ## TODO when two price points are very close (i.e. 4-5%) then take the lower one
        ## TODO fiter out the sellsides which are taken out in after time of when the liquidity was formed

    def get_nearest_sellside(self, sellsides, current_price):
        closest_so_far = 1000
        for i in sellsides:
            if abs(100*(current_price-i['price'])/current_price) < closest_so_far:
                closest_liquidity_price = i['price']
                closest_so_far = abs(100*(current_price-i['price'])/current_price)
        return {'closest_liquidity_price': closest_liquidity_price, 'percentage': closest_so_far}
    
    def get_if_near_sellside(self, data, percentage, num_neighbours=1):
        sellsides = self.find_sellside_liquidity(data, num_neighbours)
        if sellsides!=[]:
            nearest_sellside = self.get_nearest_sellside(sellsides, data[-1]['close'])
            if nearest_sellside['percentage'] <= percentage:
                return {'nearest_liquidity_in_range': nearest_sellside['closest_liquidity_price']}
            else:
                return {'nearest_liquidity_in_range': 0}
        else:
            return {'nearest_liquidity_in_range': 0}
        
