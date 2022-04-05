'''
@ WECHAT / TELEGRAM    :   MGSJZLS
@ Youtube Channel      :   youtube.com/c/美股数据张老师

群里问得最多的 MACD KDJ RSI 今天代码打包
返回量价齐升 
返回涨幅大于N 
返回成交额大于N 
获取某只标的的 可卖数量 	本代码为粉丝在YT频道留言后 整理上传GITHUB
'''

def idc_rate(df_idc, N):
# 传入snapshot数组 返回涨幅大于N的dataFrame
	df_rate = df_idc[df_idc['rate'] >= N]
		return(df_rate)

def idc_turn(df_idc, N):
# 传入snapshot数组 返回成交额大于N的dataFrame
	df_rate = df_idc[df_idc['turnover'] >= N]
	return(df_rate)

def idc_pv(df_idc_, df_m1, N):
# 传入snapshot数组 和 1分钟k线数据 返回量价齐升的dataFrame
	df_idc = df_idc_.copy()
	start = 0;		codes=[];		old_N = N - 1
	df_find = pd.DataFrame({})
	for symbol in list(df_idc['code']):
		df_pv = df_m1[df_m1['code']==symbol]
		df_pv['turn1'] = df_pv['turnover'].shift(-1) - df_pv['turnover'].copy()
		df_pv['last1'] = df_pv['last_price'].shift(-1) - df_pv['last_price'].copy()
		df_pv.reset_index(drop=True, inplace=True)
		df_pv['turn1'] = df_pv['turn1'].shift(1).copy()
		df_pv['last1'] = df_pv['last1'].shift(1).copy()

		if len(df_pv) <= old_N:
			continue
		while N > 1:	
			if (df_pv['last1'].iloc[-1-start] > df_pv['last1'].iloc[-1-start-1] and 
			df_pv['turn1'].iloc[-1-start] > df_pv['turn1'].iloc[-1-start-1]):
				start += 1
			else:				
				break
			N -= 1
		if start == old_N:
			df_find = df_find.append(df_pv.iloc[-1])
	return(df_find)

def kdj(data):
	N=9;M1=3
	data['llv_low']=data['low'].rolling(N).min()
	data['hhv_high']=data['high'].rolling(N).max()
	data['rsv']=(data['close']-data['llv_low'])/(data['hhv_high']-data['llv_low'])
	data['k']=(data['rsv'].ewm(adjust=False,alpha=1/M1).mean())
	data['d']=(data['k'].ewm(adjust=False,alpha=1/M1).mean())
	data['j']=3*data['k']-2*data['d']

	for j in range(8):
		data['k'].iloc[j]=0
		data['d'].iloc[j]=0
		data['j'].iloc[j]=0

	data['k'] =data.apply(lambda x: int(x['k']*100), axis=1)
	data['d'] =data.apply(lambda x: int(x['d']*100), axis=1)
	data['j'] =data.apply(lambda x: int(x['j']*100), axis=1)
	
	return data
	
def macd(df_macd):
	df = df_macd.copy()
	df['short'] = df['close'].ewm(span=12, adjust=False).mean()
	df['long'] = df['close'].ewm(span=26, adjust=False).mean()
	df['dif'] = df['short'] - df['long']
	df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
	df['macd'] = (df['dif'] - df['dea']) * 2

	return(df)
	
def rsi(df):
	A = pd.Series(rsix(df,6),name='RSI6')
	B = pd.Series(rsix(df,12),name='RSI12')
	C = pd.Series(rsix(df,24),name='RSI24')
	df = df.join(A)
	df = df.join(B)
	df = df.join(C)
	return(df)
	
def get_pos(TRD_ENV):
# TRD_ENV 传入 'SIMULATE' or 'REAL'
# 返回can_sell_qty大于0的dataFrame
	data_pos = pd.DataFrame({})
	ret,data_pos = trd_ctx.position_list_query(trd_env=TRD_ENV,refresh_cache=True)
	if ret == RET_OK and len(data_pos)>0 and data_pos['can_sell_qty'].iloc[-1]>0:
		df = data_pos[['code','can_sell_qty','cost_price','nominal_price']].copy()
		df = df[df['can_sell_qty']>0].copy()
		return(df)
	return data_pos
	
def get_one(symbol,TRD_ENV):
# TRD_ENV 传入 'SIMULATE' or 'REAL'
# 获取某只标的的 可卖数量
	ret,data_pos = trd_ctx.position_list_query(code=symbol, trd_env=TRD_ENV, refresh_cache=True)
	if ret==-1:
		print('position_list_query error')
		return 0
	pos_num=data_pos['can_sell_qty'].iloc[-1]
	return(pos_num)
	
