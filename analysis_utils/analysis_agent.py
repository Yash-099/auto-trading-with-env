class AnalysisAgent:
    def find_fvg_bisi(self, data, remove_rebalanced=True):
        bisi = []
        for i in range(len(data)):
            if i == 0 or i == len(data)-1 or i == len(data)-2:
                continue
            else:
                if data[i-1]['high'] < data[i+1]['low']:
                    bisi.append({'low': data[i-1]['high'], 'high': data[i+1]['low'], 'datetime': data[i]['datetime'], 'type':'bisi'})
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

    def find_fvg_sibi(self, data, remove_rebalanced=True):
        sibi = []
        for i in range(len(data)):
            if i == 0 or i == len(data)-1 or i == len(data)-2:
                continue
            else:
                if data[i-1]['low'] > data[i+1]['high']:
                    sibi.append({'low': data[i+1]['high'], 'high': data[i-1]['low'], 'datetime':data[i]['datetime'], 'type':'sibi'})
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
                            break
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
  
    def get_swings(self, data, side, strong=True):
        swings = []
        def get_closest(swings):
            current_price = data[-1]['close']
            closest_so_far = float('inf')
            for i in swings:
                if abs(current_price - i) < closest_so_far:
                    closest_price = i
                    closest_so_far = abs(current_price - i)
            return closest_price
        if side == 'up':
            if strong:
                for i in range(2, len(data)-2):
                    candle_high = data[i]['high']
                    previous_high = data[i-1]['high']
                    previous_high_2 = data[i-2]['high']
                    next_high = data[i+1]['high']
                    next_high_2 = data[i+2]['high']
                    if candle_high >= max(previous_high, next_high, previous_high_2, next_high_2):
                        swings.append(candle_high)
                    
                    # remove purged
                    for i in swings:
                        if candle_high > i:
                            swings.remove(i)
            else:
                for i in range(2, len(data)-2):
                    candle_high = data[i]['high']
                    previous_high = data[i-1]['high']
                    next_high = data[i+1]['high']
                    if candle_high >= max(previous_high, next_high):
                        swings.append(candle_high)
                    
                    # remove purged
                    for i in swings:
                        if candle_high > i:
                            swings.remove(i)

        elif side == 'down':
            if strong:
                for i in range(2, len(data)-2):
                    candle_low = data[i]['low']
                    previous_low = data[i-1]['low']
                    previous_low_2 = data[i-2]['low']
                    next_low = data[i+1]['low']
                    next_low_2 = data[i+2]['low']
                    if candle_low <= min(previous_low, next_low, previous_low_2, next_low_2):
                        swings.append(candle_low)
                    
                    # remove purged
                    for i in swings:
                        if candle_low < i:
                            swings.remove(i)
            else:
                for i in range(2, len(data)-2):
                    candle_low = data[i]['low']
                    previous_low = data[i-1]['low']
                    next_low = data[i+1]['low']
                    if candle_low <= min(previous_low,next_low):
                        swings.append(candle_low)
                    
                    # remove purged
                    for i in swings:
                        if candle_low < i:
                            swings.remove(i)

        else:
            raise Exception('side should be either up or down')
    
        return list(set(swings)), get_closest(swings)