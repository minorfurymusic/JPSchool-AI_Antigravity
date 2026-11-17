"""Comprar no dia seguinte ao sinal ou esperar k pregões? Conservadoras (C1 25%, C2 20%), operações fechadas.
Mesma data e preço de saída; muda só o dia da compra. Lê cons_ops.pkl salvo de estudos/kairi_sinais_conservadoras.py (variável O)."""
import pandas as pd, numpy as np
S='/tmp/claude-0/-home-user-JPSchool-AI-Antigravity/fd72a53f-617a-5c36-a0e6-2a1ebd0f529f/scratchpad/'
O=pd.read_pickle(S+'cons_ops.pkl')
for c in ['sinal','entrada','saida']: O[c]=pd.to_datetime(O[c])
FIM=pd.Timestamp('2026-11-09'); O['saida_f']=O.saida.fillna(FIM)
P=pd.concat([pd.read_csv(f'planilhas/precos_{a}.csv',sep=';',decimal=',',encoding='utf-8-sig',usecols=['data','fundo','abertura','fechamento','negociou (1/0)']) for a in range(2017,2027)])
P['data']=pd.to_datetime(P.data,dayfirst=True); P=P.sort_values(['fundo','data'])
P['mm200']=P.groupby('fundo').fechamento.transform(lambda s:s.rolling(200).mean().shift(1))
R=pd.read_csv('planilhas/rendimentos_pagamentos.csv',sep=';',decimal=',',encoding='utf-8-sig'); R['data_base']=pd.to_datetime(R.data_base,dayfirst=True)
def rend(f,a,b): r=R[(R.fundo==f)&(R.data_base>=a)&(R.data_base<b)]; return float(r['valor (R$/cota)'].sum())
G={f:g.set_index('data') for f,g in P.groupby('fundo')}
K=[0,1,2,3,5,10,15,20,30]
rows=[]
for o in O[O.status=='Fechada'].itertuples():
    g=G[o.fundo]; g=g[g['negociou (1/0)']==1]
    seg=g.loc[o.entrada:o.saida_f]
    px_s=o.preco_saida
    r={}
    for k in K:
        if k>=len(seg)-1: r[k]=np.nan; continue
        d=seg.index[k]; ab=seg.abertura.iloc[k]
        r[k]=(px_s+rend(o.fundo,d,o.saida_f))/ab-1
    lows=seg.fechamento.iloc[:31]/o.preco_entrada-1
    rows.append(dict(fundo=o.fundo,entrada=o.entrada,res0=r[0],**{f'k{k}':r[k] for k in K},
                     fundo_30d=lows.min(), dia_fundo=int(lows.values.argmin()),
                     abaixo_dia5=float(seg.abertura.iloc[5]<o.preco_entrada) if len(seg)>5 else np.nan))
D=pd.DataFrame(rows)
print('operações fechadas:',len(D))
t=pd.DataFrame({'dia da compra (pregões depois do 1º dia)':K,
  'resultado médio':[D[f'k{k}'].mean() for k in K],'mediana':[D[f'k{k}'].median() for k in K],
  'pior':[D[f'k{k}'].min() for k in K],
  'melhor que comprar no 1º dia (%)':[(D[f'k{k}']>D.k0).mean() for k in K]})
print(t.round(3).to_string(index=False))
print('queda máxima nos 30 pregões após a compra: média %.1f%%, mediana %.1f%%; dia típico do fundo: %d (mediana)'%(100*D.fundo_30d.mean(),100*D.fundo_30d.median(),D.dia_fundo.median()))
print('fração que caiu mais 3%%+: %.0f%%, 5%%+: %.0f%%, 10%%+: %.0f%%'%tuple(100*(D.fundo_30d<=-x).mean() for x in (0.03,0.05,0.10)))
D.to_pickle(S+'espera.pkl')
