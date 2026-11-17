"""Análise rápida: vale vender um fundo com lucro para entrar num sinal novo? (conservadoras: C1 25%, C2 20%)

Lê as operações salvas por estudos/kairi_sinais_conservadoras.py (rodar antes, salvando O em cons_ops.pkl no caminho S)
e compara, para cada sinal novo que aparece com outro fundo comprado: segurar até a saída contra vender e trocar,
medindo os dois caminhos na mesma data final (a mais tarde das duas saídas), com o 105% do CDI depois da saída. Antes do imposto."""
import pandas as pd, numpy as np
S='/tmp/claude-0/-home-user-JPSchool-AI-Antigravity/fd72a53f-617a-5c36-a0e6-2a1ebd0f529f/scratchpad/'
O=pd.read_pickle(S+'cons_ops.pkl')
for c in ['sinal','entrada','saida']: O[c]=pd.to_datetime(O[c])
FIM=pd.Timestamp('2026-11-09')
P=pd.concat([pd.read_csv(f'planilhas/precos_{a}.csv',sep=';',decimal=',',encoding='utf-8-sig',usecols=['data','fundo','abertura','fechamento']) for a in range(2018,2027)])
P['data']=pd.to_datetime(P.data,dayfirst=True); P=P.set_index(['fundo','data']).sort_index()
R=pd.read_csv('planilhas/rendimentos_pagamentos.csv',sep=';',decimal=',',encoding='utf-8-sig'); R['data_base']=pd.to_datetime(R.data_base,dayfirst=True)
cdi=pd.read_csv('planilhas/cdi.csv',sep=';',decimal=',',encoding='utf-8-sig'); cdi['data']=pd.to_datetime(cdi.data,dayfirst=True); I=cdi.set_index('data')['indice_105_do_cdi']
def ind(d): return float(I.loc[:d].iloc[-1])
def rend(f,a,b): r=R[(R.fundo==f)&(R.data_base>=a)&(R.data_base<b)]; return float(r['valor (R$/cota)'].sum())
def preco(f,d,col): 
    s=P.loc[f][col]; s=s.loc[:d]; return float(s.iloc[-1])
TX=0.0003
O['saida_f']=O.saida.fillna(FIM)
O['px_fim']=[r.preco_saida if pd.notna(r.preco_saida) else preco(r.fundo,FIM,'fechamento') for r in O.itertuples()]
O['rend_tot']=[rend(r.fundo,r.entrada,r.saida_f) for r in O.itertuples()]
rows=[]
for h in O.itertuples():
    for n in O.itertuples():
        if n.fundo==h.fundo or not (h.entrada < n.sinal < h.saida_f): continue
        d=n.entrada
        if d>=h.saida_f: continue
        px_now=preco(h.fundo,d,'abertura'); r_ate=rend(h.fundo,h.entrada,d)
        lucro=(px_now+r_ate)/h.preco_entrada-1
        T=max(h.saida_f,n.saida_f)
        # 1 real de posição h marcado a mercado em d
        hold=( (h.px_fim*(1-TX) + (h.rend_tot-r_ate)) / px_now ) * ind(T)/ind(h.saida_f)
        caixa=(1-TX)*(1-TX)  # vende h e compra n
        sw=caixa*((n.px_fim*(1-TX)+n.rend_tot)/n.preco_entrada) * ind(T)/ind(n.saida_f)
        rows.append(dict(seg=h.fundo, ent_seg=h.entrada.date(), novo=n.fundo, sinal_novo=n.sinal.date(), dias_no_seg=(d-h.entrada).days,
                         lucro_agora=lucro, resto_seg=(h.px_fim+h.rend_tot-r_ate)/px_now-1, novo_res=(n.px_fim+n.rend_tot)/n.preco_entrada-1,
                         fim=T.date(), vantagem_troca=sw-hold))
D=pd.DataFrame(rows)
D.to_pickle(S+'troca.pkl')
print('pares (sinal novo enquanto outro fundo está comprado):',len(D))
D['faixa']=pd.cut(D.lucro_agora,[-1,0,0.05,0.10,0.15,0.20,5],labels=['prejuízo','0-5%','5-10%','10-15%','15-20%','>20%'])
t=D.groupby('faixa',observed=False).agg(pares=('novo','size'),dias_no_seg=('dias_no_seg','median'),resto_seg=('resto_seg','mean'),novo=('novo_res','mean'),vant=('vantagem_troca','mean'),troca_ganha=('vantagem_troca',lambda s:(s>0).mean()))
print(t.round(3).to_string())
print(D[D.lucro_agora>0].sort_values('sinal_novo')[['seg','ent_seg','novo','sinal_novo','dias_no_seg','lucro_agora','resto_seg','novo_res','vantagem_troca']].round(3).to_string(index=False))
D.drop(columns='faixa').to_csv('planilhas/tecnico/kairi_troca_pares.csv', sep=';', decimal=',', index=False, encoding='utf-8-sig')
