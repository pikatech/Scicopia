#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import sys
from flask import current_app
from werkzeug.security import generate_password_hash

from datetime import datetime

from elasticsearch_dsl import (
    Boolean,
    Completion,
    Date,
    Document,
    Keyword,
    Short,
    Text,
    connections,
)
from elasticsearch.exceptions import ConnectionTimeout
from elasticsearch.helpers import streaming_bulk
from pyArango.theExceptions import DocumentNotFoundError
from tqdm import tqdm

from scicopia.config import read_config
from scicopia.exceptions import (
    ConfigError,
    DBError,
    ScicopiaException,
    SearchError,
)
from scicopia.utils.arangodb import connect, get_docs, select_db

logger = logging.getLogger("scicopia")
logger.setLevel(logging.INFO)


config = read_config()
# use a spezial config for the tests


def setup():
    """
    Connect to the Arango database and Elasticsearch.

    Returns
    -------
    Connection, Database, list
        1. The connection to Elasticsearch
        2. The ArangoDB database that holds the collection
        3. The list of fields that are take over from ArangoDB to Elasticsearch

    Raises
    ------
    ConfigError
        If a required entry is missing in the config file.
    DBError
        If the connection to the ArangoDB server failed or the database
        or the collection can not be found.
    SearchError
        If the connection to the Elasticsearch server failed.
    """

    if not "es_hosts" in config:
        raise ConfigError("Setting missing in config file: 'es_hosts'.")
    conn = connections.create_connection(hosts=config["es_hosts"])
    if not conn.ping():
        raise SearchError("Connection to the Elasticsearch server failed.")
    try:
        arangoconn = connect(config)
        db = select_db(config, arangoconn)

    except (ConfigError, DBError) as e:
        logger.error(e)
        raise e

    return conn, db, config["fields"]

# Used to declare the structure of documents and to
# initialize the Elasticsearch index with the correct data types
class Bibdoc(Document):
    entrytype = Keyword()
    author = Keyword(multi=True)
    editor = Keyword(multi=True)
    publisher = Keyword()
    institution = Keyword()
    title = Text()
    title_suggest = Completion()
    booktitle = Text()
    abstract = Text()
    keywords = Keyword()
    tags = Keyword()
    year = Short()
    date = Keyword()
    pages = Keyword()
    journal = Text()
    volume = Keyword()
    number = Keyword()
    graph = Boolean()
    doi = Keyword()
    created_at = Date()

    class Index:
        name = config["index"]

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)

def setupElasticsearch(data, allowed):
    Bibdoc.init()

    try:
        for key, entry in data.items():
            doc = Bibdoc(meta={"id": key})
            if "cited_by" in entry or "citing" in entry:
                doc["graph"] = True
            for field in allowed:
                if field == "year" and "year" in entry:
                    year = entry[field]
                    try:
                        doc["year"] = int(year)
                    except ValueError:
                        logging.warning("Can't parse year %s in document %s", year, key)
                        continue
                elif field == "abstract":
                    if field in entry:
                        abstract = entry[field]
                        if "abstract_offsets" in entry:
                            doc["abstract"] = [
                                abstract[start:end]
                                for start, end in entry["abstract_offsets"]
                            ]
                        else:
                            logging.warning(
                                f"No offset for saving abstract in '{key}'."
                            )
                else:
                    if field in entry:
                        doc[field] = entry[field]
            doc.save()
    except ConnectionTimeout as e:
        logger.warning(
            "Timeout occurred while indexing"
        )
        logger.warning(e)
    except DocumentNotFoundError:
        pass
    pass

def setupArangoDBDocuments(collection, data):
    for key, entry in data.items():
        if key == "miss":
            continue
        doc = collection.createDocument()
        doc._key = key
        for key, value in entry.items():
            doc[key] = value
        doc.save()

def setupArangoDBUser(collection):
    doc = collection.createDocument()
    doc._key = "exists"
    doc["username"] = "Test"
    doc["email"] = "test@email.de"
    doc["password_hash"] = generate_password_hash("test")
    doc["lastsearch"] = []
    doc["confirmed"] = False
    doc.save()
    doc = collection.createDocument()
    doc._key = "exists2"
    doc["username"] = "Test2"
    doc["email"] = "test2@email.de"
    doc["password_hash"] = generate_password_hash("test2")
    doc["lastsearch"] = ["Lorem", "lorem", "loreM", "ipsum", "Ipsum"]
    doc["confirmed"] = True
    doc.save()

def setupArangoDBPDF(collection):
    doc = collection.createDocument()
    doc._key = "121518513"
    doc["pdf"] ="B~V00Eio=N3MJ6g#n=inATS_rVrmLJJPI#NWo~D5XdpB=HXtA%ARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-rlhJ#X7E5QcaE3XK#HtLBF!du)MbD7sZ!k%5+2gN;NwA{ik6zP#fpiQCSdI_bST-ti^*K%a))hkM>toHwVo71i*gQk`nLR#m-h8!mY@Ox1VB>xbb>wU-^_L>9d1+qTrc`qeD;UZ{@QYe*y~Kl`=FU}F(_G4Za*(Ys)xiD_G-r`$Z+de51wIlDl*XJ)o>rIuhO8f`Ug;=HRx&+?w)$X<#^-ZyP~%3swe)fJ1zu8YqtJ<B7c;w+lwn&Tq_kC3nqMm*#GQ>wv4UL8v@(RbEoYBD8ZsDOv1+@dc|7pZ6alwM#E7{-QG!wrDM<47gSalrcF*7P$p`Z--=(oNp?bYLIJ6lg4))tAWlK!VD8grkfp;9b2d{7fNI)08%W{%<B^ue!vmIj4mTe2d$dF~5wyu}wHU)~#YX<ijbE-!Yx>-pzVhjk_yJ=gT+179gU2w2O`u1?|R|LJ3TWMG$5n2{Vv{8Mawk379p1yHOe;PjVXpl16~U5g>?Eknc&wHAJerlz2lFYxt%x6A=Z4h#nEqo)A6!hx4Dq+5HZu6y2Y2LK5JVIf-yW;tfuSUg3l_2q$DWvc&5@5Xu`_g8qRZGFfo;m|qbY-F+T*zW}}|dl?F4Ze(+Ga%Ev{3T19&Z(?c+G9WM@Z(?c+JUj|7RC#b^ATLm1XJra6LvL<$Wo~qHATuB^AW{l1Qe|^*b#h~6b09GwFd$M2FHL1+X<<TdcpzIaATS^`IW-_SG%{TZFHm7}Wo~pJH6Sn`QVKpk3T19&Z(?c+F(5D?Z(?c+JUj|7MsIF(AUr%EFGevoAT%H_AW|ScJ_;{Ta&Kc(Wpp50ATLlvMj$U#Wq5QTT?#%v3T19&Z(?c+HXtw{Z(?c+JUj|7Ol59obZ8(kGd3U~ARr(hAPO%=X>4?5av(28Y+-a|L}g=dWMv9IJ_>Vma%Ev{3V7NxGS@S(P%u!iP|!8BR4_77Ff>p|G2|-bGBgB=8Ymc9LZy;(xtu(?^urYl4Y~9^fZ|;Gp1uktMWv}+`c47P3P4d8g=nCrST0W&1v!TLhW`!!4*=l<5UhV7m%spn4;T)BAmahX2IdB426hHE20jKE1`CD)pd^>8Cs!aB0QU(et_o#tWOH<KWnpa!Wo~3|VrmLEATS_rVrmLJJPI#NWo~D5XdpQ?ARr(hARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-k{E*E6tCFi-$tLrVoi1BDbru0k##4T6RciR4@^Cr>W@a3G&c-vdl~`YMzZm8Np(I|Vo^7;@>mC`2177{qdUx+uso)Hl>O{67GJAhsL>m#ZgNAQu1!jU3AgWo~41baG{3Z3<;>WN%_>3OFDzAa7!73OqatFHB`_XLM*FGBr0KARr(hARr1aMrmwxWpW@dMr>hpWkh9TZ)9Z(K0XR_baG{3Z3=kWb<nYD!!QsA;1hxvj)2x=@;yN<6L9DhNK&YWLOXRRg+QAzkd_9rIgjQ?@grpPVC<e`4V4-l7JMfO^PiTBJAF@@7QB}H<@A~37ZwHgwlxPI2V9q!y;4zN_Q<=Kl~45ZecEHTe%=uGTYAe$zhk*2;HqIP(L^DyQ6y~?s*7UYN1=xh$Kf(!SA}RQm%d&F5cO(IFD_{S3F*~A1(<+p9g+Z3kX-~b5Pbw1VDNEd*z`Mq$_K|A=NY&>2!qBB0g!r-yzD#%%EQE<bx1r+&Asj>X6EnxO=z3xFU}U6rF9VYNjS7J$C5+a;1$pDANWw>3;qK5=7mfOWo~41baG{3Z3<;>WN%_>3OOJ!Aa7!73OqatFHB`_XLM*FF*PzEARr(hARr1aMrmwxWpW@dMr>hpWkh9TZ)9Z(K0XR_baG{3Z3=kWGc(Y$G*U27Facsya|JUCg%m@sLM~H~m;s0jl1R?wa`NQT4_7cX;?nm3igM|D`YMzZm8Np(I|Vo^7;@>mC`2177{qdUx+whr|NjRA0|P3>`2PU|2-F{dPz|FLh%&%K6+oy2!qfvS6ypJ8iWx$&qfq=1${s@1gDJ-U2Y`q{{(r-NFhHZYTs^r0xd8Q2fTId!Ze(+Ga%Ev{3T19&Z(?c+F)$!7Aa7!73OqatFHB`_XLM*FGB`OPARr(hARr1aMrmwxWpW@dMr>hpWkh9TZ)9Z(K0XR_baG{3Z3=kWWzaiL!$1%Q;NNm#X`4NQ=K^3maTL+8QV0?*kf5SKR6t1qf-XvY6Rxs1VUOU_h{(gvB+5f+KFhQ7*qupzUQMZ_37w6ozMyGIFO_*W^*9DgnvOOn&u?bdnBsxzu_<n1*c8nzeSUnsnqqc$MU^S$^jJ~(WSTi4VWfcNkO7YS=zzf@>5*Gx0ogY)kMsw&mE0Tv!$nuPj5;iL=2)ofs68+{a@d(}<pWnOq_<at=z3LBk+Xy>YY&#6lsUFdn58`G<rUmX68Czr);g(3c-urwxz&))W51v3)O=%*k3BIvGMw0nUbMd7+v;7~LAS)ZH<`c0Uu?9-ZzpT-7DzjE&f9<xU(q7y#XVeXXs#P`Z~g&Sj*8F<Wo~41baG{3Z3<;>WN%_>3NbMtFd%PYY6?6&3NK7$ZfA68ATlyJARr(hARr(LFGgu>bY*fNFGg%(bY(<kV{c?-3O+sxb98cLVQmU{+I7#dN&`U<2H=0WVqpsJ4ZL{)-5l9yx`i0QD+H}lh!9Xq3q?CI3%=NNzQ(<QvAg1MoxKx_pi_LsKRZ9HpC2C2c*33!YW8#XGrq0qf&5fMjgQ97%{?s|ax3;za%UQoYtH%U@%fJ2;^KsBa!bCdd2&t7l3{!3gcQ}TY=J_GEns0fU=PrBDR>2{78`Yo5O=NQN4-~znAQ2mGN~qI%deaS$)@49&)RNi8=HsDAlc1m{B@o1hhfL4hiiTRp$gtx31ZZ$wQrwdyZs_XlX{bePriUo8@i-#$&74a3T19&b98cLVQmU!Ze(v_Y6>wjATS_rVrmLJJPI#NWo~D5Xdp5%Gaw)!ARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-qC$u?oU45C-5o916Gi2)!53G*~TyP^b!a5Oi`7Cv_B5bd@|>AEmxQ!9_4ylU7u8bTGp=+>zY<r0LgXz#ccaCb=oO)#iny4f(d{aq#HOR}{r0ChP|!2Bu6R9`bIxUy_JMU6v$zJeBOtDDE+8Fem@gDXbLYAGDKES94|TIH_@sXTWO;2cv=z(DYn|Ie?qs4WOFZyH08LvT}Y?zr@np&+5;Y-zPpdDL1qxkDV_7p~920iH-?qz%;WNlOnHjO}_F6s2|gq?s{a0+6rZEWOH<KWnpa!Wo~3|VrmL8GaxV^Z(?c+JUj|7Ol59obZ8(lFf$+^ARr(hAPO%=X>4?5av(28Y+-a|L}g=dWMv9IJ_>Vma%Ev{3V7O`kG%@QFcgJP=@7U}-@x7%(6pp>4fq3g5Oi`7K~P6QMZrNZkCsR2BRDz;^~N9E9r8g=$hqGwOvf0`*l;`NBIBaV>zwvvN(tp!zF$^b>Q$s?Y)aB2iAh&uJ|0dR(!EKabJ7Ez=bSC58ZdBmK-}Db#9si51b85J(H)VG?~<w;(puH9brO*JFRXhb_0pkUMIXpP^B-P+e^vI2%zA;$#ZEM^45&p7K{E298#@tKVTBgN=?ti_78(Z{Ry3t2R%lFe3T19&b98cLVQmU!Ze(v_Y6>wlATS_rVrmLJJPI#NWo~D5Xdp5%G9VxzARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-p<su?~VT5C-6q4kS0g3z&E>prsKcP9%tl3?@1`7$<df(CB6?kH(|$2#gFyyn=?t)x-|paM$+!3;dxB(ZdlABnA@46WmKUfv<}mhVRbq2yqHxjeZDXPGu130x#$50Yto<q6CrPMxwWcG(kp3X`=dDtC6*;KdUm5*CpxZH!@-ld1p5Hpbq1ePH2}pp<QU*Lci_jol(}QOq(h7&$j=VKbsTHByRpm*kq>UywqD*6>XH!Mvls9$DVr9)r#bGK{hjBmcj~Nw$W<43T19&b98cLVQmU!Ze(v_Y6>wmATS_rVrmLJJPI#NWo~D5Xdp5%Fd!fxARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-nQ(F>1pw7zN;GJP7{9H;DfWG_sN7F$O1vdMKn*hY$!P84FEF*H}l>QGA4q8A{z(ToWi%h!6Ax`kx9nbxt#N`jBgpX))7%E=O@CLmtcFX7?s_BlcBYDfWr6*ydT!r;mf!dbQA8>{8dcW*cdiis%b~=>w3)SKxwAa9<GJP=QGW(;@W<2}wW_(jO|1q$6gaCD#@s{U5k~;Vk@1d&iGdBN^uoyt4+jEQHRmabU?Pux{*G+yHY-_!)l#;=UW+md8e3<Qs#xRx%1@Ze(+Ga%Ev{3T19&Z(?c+F*YDDAa7!73OqatFHB`_XLM*FGB-6KARr(hARr1aMrmwxWpW@dMr>hpWkh9TZ)9Z(K0XR_baG{3Z3=kWosYjx!!QuWKPy8dFMfpF3qTTZOQ%*UMIr+dOdSvtFfxE(s~Y#o$fHE!1w3}JdYtV_42T8C`o+3G-+gCirxz1y=$uZ@TCy{;6MAa(tF~664Na%V)Z>d@cDi1ZwYt8RxURb!dVl+P*7frCl3HD_=)R@qL3b;H9OIw@`VoeA-eXaI?L30w!mB+F$`>A6HI^PdP>xtghtR<cs2r-{KR5SgovfMl<19et24RpticiU-Fzlp8d<vuKBh7ERlpPYsMCPc&%$Xw;r%=xv()$qW4X0j?X2jN9Sh-D995VMw_b-N@O1DkDNkKkfo|HGykE|p&8tdcksARaTDyE>XI(?_V0VE86SPErsWOH<KWnpa!Wo~3|VrmL8Hy|(|Z(?c+JUj|7Ol59obZ8(kGBqF|ARr(hAPO%=X>4?5av(28Y+-a|L}g=dWMv9IJ_>Vma%Ev{3V7NxGS@S(P%uz124W*q1v7Jn6hp2;E+a!A-vGn~NhIfTIeBvFhbtHva_M^jMY;4neHBWIN>jP?odTQ{fTAu6(LgP+T%Ilpj1L&te}EAG9|VGk0HufojDHyZ!w~x)2IfB?5jr5|e+>Ws|9~JaS5K}$E&#g~PzefUZe(+Ga%Ev{3T19&Z(?c+F*qPFAa7!73OqatFHB`_XLM*FF*Y$EARr(hARr1aMrmwxWpW@dMr>hpWkh9TZ)9Z(K0XR_baG{3Z3=kWGqTh(w^T4t&^1-iH8M~zGE^`#S4c7BD&#UU1qvG|SeV1)l5@G7Jh}A46^u-|^gVzQT>75A3MECQsa*O_0nQ4BT>35w(S`~Jv0R=m3JeT33=9naA(-)h0}6(TgVm4&>KhpB|06I12m{3!?1v<_1LArh{tqM}xDJZ{Fw`^rV6b8Qz#zx`fPozpeE%32xLiHC0=WRb6k9V2Wo~41baG{3Z3<;>WN%_>3Nbk#Fd%PYY6?6&3NK7$ZfA68ATlyAARr(hARr(LFGgu>bY*fNFGg%(bY(<kV{c?-3O+sxb98cLVQmU{+QrT>io!q?24F*qfmfIdEaaWQNiY$u0#U&f3vOj0R=VZFDq1Hu@JimmE93|%Q)r&^{$^!8fCKX}^Jd=TPvb!{;)sWCClek`co);2lGNQJz3RjEhw_5#ij$P=!d1x@pL{%=zRBjxDaT}IypB2AP%&fg)^kf<G|-3M`wXT2XCPWPEv(@MR%#zzA8-tRVXb->)vr{8`2oyODe)@m{i^@v+^9zF{1&}8%z?cQ3M^rU3>or-FhIhfLBi%Qxf`T*Q1oD=5@|zepQU+0U-SST`ik5NWo~41baG{3Z3<;>WN%_>3NkPtFd%PYY6?6&3NK7$ZfA68ATcp8ARr(hARr(LFGgu>bY*fNFGg%(bY(<kV{c?-3O+sxb98cLVQmU{+A}iOGq6xFP%s8!BU1%4ONA6eu0k#&Lm=M(#05zt=W;oDa_NUF7#VWudjLhb^gVqQN{UKTx%8a^oE3ngE(*~=EwNmlE((l)82-Z$`yU48KMagR4Ke>?`2YV01aY}~as_e$0FQ89+6rZEWOH<KWnpa!Wo~3|VrmL9F(5D?Z(?c+JUj|7Ol59obZ8(lFf$+^ARr(hAPO%=X>4?5av(28Y+-a|L}g=dWMv9IJ_>Vma%Ev{3V7P(&^@ZcKoAG;e@GFS!dyVeoWM=|APPdj4={zGm4#TTrJ$m%$<g*Gdj!iAtK;q~AHEa3Vus)Rrx=)F*69v7<({j2#Qi=WGP+Riv(%4%u|LtIB(>puKx*MqQst6w*ZYywWHsfC)Qq<or#mWV99RgD7(i?!#&xeaYywkxjRPCiMUBXw@opi}2(7`RjaVaiX;eeR#;Hb?{zz&RPee~ApfJDmcG7>!-S(&cvqJZcN+WI{(j+3Gi1{X(m$ar2-H)W33T19&b98cLVQmU!Ze(v_Y6>zkATS_rVrmLJJPI#NWo~D5Xdp2)IUpb)ARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-k{H(K9qxFi<cCVpBr}6BC6LL#{$D6OfnzhzpWP&gF9Q<kAmUFfr%S_W+7=>3jMrloXYwa_Kt-I4c-(>ANUI8!8yYa(TKaF#ciu$H4Ia5BvWEKvItV1CX>}{K3Hfr-1Pf1M{B;41X9H{~loY2P7Ln<o^bSdLYSwApc>Ie+Dnf4DxNm|NlSi|NlcKxm-QD0=WP`acWZvWo~41baG{3Z3<;>WN%_>3NkYwFd%PYY6?6&3NK7$ZfA68ATlsHARr(hARr(LFGgu>bY*fNFGg%(bY(<kV{c?-3O+sxb98cLVQmU{+MSR+3c^4Tg-22ZrpXa97tl>~{izgU1XBoFS%{TdS}59y$<cBYkB~A&NPL?pD0af|?aZ6qowut;onc=*=}FrcJrLcOz0W7sU5K7h>dx-SLBwh;y31+~nN_rq%lUd>6)dOXvkGP7i?`({6rwmGBCE<kCoRA+x!{c)G;*?2YGq_SOdvrC(E*DWU2MD41dQLr@d;Ki`DJC8{>QJ|%&g>dZsWv-tMcs-o(r<UoUF_Q5|l6V%}d?11nnvZ>)+s6#4CORQ2Saw3T19&b98cLVQmU!Ze(v_Y6>zmATS_rVrmLJJPI#NWo~D5Xdp5%I3OS(ARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-pPdy^g{#3<q#q9V&V0Bj6W+G$MeIkdXM0=zw%L-Eg`I7?A+M3Vk#lrH|0DLr8E)CvLo3euJ$ze|unhdc-;RxvR%K&}<BEH66)>YR<!c+uH1DR*?E)Ga|K;I;mpK=hJ0JYW6W_O=`j4n)4qj7K}Er0N!T46enpV9<YJ*QGo+|lyC!--n2vy(7B@%E0i}`v<{}xCYVI+yXgMv@0sz(*1FB(UfJ9$tz@1?%do{&HoAiav~|*mldKXu(usEn6aL%81-)<Hq-8;$^aLc7ikb>#Ze(+Ga%Ev{3T19&Z(?c+GBqGDAa7!73OqatFHB`_XLM*FGBPzFARr(hARr1aMrmwxWpW@dMr>hpWkh9TZ)9Z(K0XR_baG{3Z3=kWt<SM)0znW4;QzSdU<&UAgqs&g_7>MWtQL#`uMo7d2&tlFiim+!?!8GKB|eIekn)P)I^GJ3mZtdzW|x_N`ufonoO6#K^nm-Cjp2o+4>F~6b1r(Pr?+<+R;1=^N>XF#ld2}XUVSb}4X016NsahLbN))zhyho}K<sx3knX-jTX$1ngO2!zBtzUF{zlRu`a$xG$je8-BMWYiTG5?!^|c=NdOOqB=Z#sg%@eYvZO)MPnBOCkTO6=QN3`gQ>9%q0?Jn#9+WP-`$qMWDm(p`ZGdcjs_-CUEWo~41baG{3Z3<;>WN%_>3NkhzFd%PYY6?6&3NK7$ZfA68ATcyFARr(hARr(LFGgu>bY*fNFGg%(bY(<kV{c?-3O+sxb98cLVQmU{+A}uSvoumLP%s8zGX)b9g%m@sLM~&Fm;s0jl1R?wa`NQT4_7cY;?nm3igM|D`YMzZm8Np(I|Vo^7;@>mC`2177{qdUx+pOJVE*v`hy0)aKWyy&|0t+u|MB2I^UnkS8GknXXZ#Jq40S+k!}y<pf$<+2{zH4r47B(E|9^1I<?6{5$OQn%_E72yWo~41baG{3Z3<;>WN%_>3Nkk!Fd%PYY6?6&3NK7$ZfA68ATlvCARr(hARr(LFGgu>bY*fNFGg%(bY(<kV{c?-3O+sxb98cLVQmU{+D*-|PQySD1kkZuMB3)sRAheu9P1L~A|g@<5-yNPMS-Y*k^%&hi-`Es{3-VdhiI;_yo@0Q#cO6~w7xo9oa<b@o|fvDx>)K{DX-#7hI8fZ_wx86n_7xH^`#WojHRe=^!@GQS&Gf=r83>>JvR?hZx!n>&8)8`Vb(b0=>%C?0cj634JDvDnvVLTfvg1%9Whv2z|49$Gfd37+!&ZehMbKYTY29h8#oz#hCdgh_z%k~miN@~PcmfjyUoK_bZs~c=v;(c)v}Wxbr@OO3T19&b98cLVQmU!Ze(v_Y6>zqATS_rVrmLJJPI#NWo~D5Xdp2*Fd!fxARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-k{I*RwQIFi<d3&^1&rHdZh*R7f%8D&#UYPyj(QBZy3LE|-%hmwvc{u>qI92T+(x-_uv2q^LBNOW!HLS;3G?-$fzXP{AOU%hN@HfsKIy1M{I_IV5Zc#C1^okAZ;^h}nTy{{R0E|DhNpP9w}i6s}{CVW?-20AqUw3kLZH0|xm61q|#D9xyQeKfnN#;Bxik3giL+`3_2L3T19&b98cLVQmU!Ze(v_Y6>zrATS_rVrmLJJPI#NWo~D5Xdp2*G9VxzARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-qa&F$%&!5QX8lqzFu*7qFNM=w@+4%0P_Z7J^n5Vihed6a_0MN6V2sK*+iwSm+6CzT*8eshydO6Q1+baBA3EJ{r1^?Z<>|I+W^6g(JOVn~`3HnY3H;?Rr0vE;b7`q)Xl#P7dTsRxKd#Epq>5+(LOop?VBA|EvF1eZ*jgDELGyb$A&`gB%m-Fm4{ww^tBS3ux(ROK+(FVv`DGZe(+Ga%Ev{3T19&Z(?c+GcX`9Aa7!73OqatFHB`_XLM*FGB7eAARr(hARr1aMrmwxWpW@dMr>hpWkh9TZ)9Z(K0XR_baG{3Z3=kWUCliT!axuO;8_9&2GKU1a{=9~t^q5-A25ZWm4yg`S_&#!yGOFL%u#ZLlolcDZp1a%e8rnLyuRqjh(hX8TaX-(?9pD}8OtyvDL<Fp5l1od70C$s%*4p!IbAQe1M<;gOal3Y)`G$f#uL&yV>++uYk+&|6#y;8tYB>bIP0bW5IB`}s33GEa59exY>lb4nL^^sn9<Le`s%$raOS>|<uxZ1^`E-*9#ni<hmX?CY9{||CO>`kubstdj7xk2Q!z{~3T19&b98cLVQmU!Ze(v_Y6>$kATS_rVrmLJJPI#NWo~D5Xdp5)I3OS(ARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-m#qze>bF5C-sX30z<ZUYkO^c>&$cT?`5b2j>Z<5VW!o;Xo|~745{^N3yicqvR1%UJ(*^qWQzw{EC@fzL`0Wj^cz3Px)|aI6mcg#t#v_P*XLW%>G*UPqa))-*B9ezHoKY=_S9tzCV&)UY&77dd0U9n>$KZT-SxF%b|V^Y;vyxCRT|M_W)-AxbD7t0EC?uC&0qOv`#XtJ9Ff~I7im%7s_^SJ*T(z(5lK&Z{=cLaL~I62Y!o-uU;3n<2dW}?XD8oI{IfYFzlQ+e#)Ni7{9IuN>ru957`aRzWkgYG;@?qULn$XO4sxQTg_M}3T19&b98cLVQmU!Ze(v_Y6>$lATS_rVrmLJJPI#NWo~D5Xdp2&F(4oyARr(h3NJ=!Y;<LEATLI2VRU6gWn*t-WePq%3UhRFWnpa!c-k|u&@(qxFi@}nViQ9JGc$!0L#{$DV<RBn0K^4JB<FHDd2;E8D;OJb>3aZ0x%54K6-tUqQ@Qk=0-O~Lx%6EWq74-cV!1qB6c`u`7#J8nFfcFzF*6X$1M&Y44F5s+IS{i0`NIwK{{Z^)4@3R`|Nmi_%hi)BkP86JbY4ITWo~41baG{3Z3<;>WN%_>3N#=vAa7!73OqatFI0JOWgss`Z*Fu7FH?15ba`-PATLyTaAh+JFHT`?Wgss`F*XV>MsIF(O<{C$X?P%8FfK4LFfcSAFd#4>FfK4LFfcSAFd#5p3NJ=)ZgfIIZ+IYEAT2c@Eiy46H#s0TF(6$EFH&W5Z*_8GWpf}rJRmPna&Kc(Wpp50ATLlvMj$UqZDD6+LLglrK0XRBMrm?$bVF!iav(G`3NK7yb96&!VR9fbGBFA-S7~H)XmcPlGaxV^QVK6cZewp`X>MmAGc+JDAW{l1Lug@gP;zf$b09M{ATS_O3O+sxWo~3|VrmLAGaxV^Z(?c+TQWB;FgPGEATl>DFgPGEATS^_I4(CeATS^>ATS^>ATS^>ATS^>ATS^>ATS^>ATS^>ATS^|GcGVWATS^>ATS^>ATS^>ATS^>ATS^>AT}^AIWizHATS^>ATS^>ATS^`G%hhWATS^>ATS^>ATS^>ATS^>ATS^>ATS^>ATS^_I4(CeAT=~DF*hJIGcGeTAT=~DF*hJIGcGeTATS^_I4(CeATS^@H!d(ZATl{FH#s0RF)lPVATl>DFgPGMF)lJSAT=~DF*hJII4(CeAT=~DF*hJJF)lPVATu{EIWizKI4(3cATu{EIWizMG%hhWAT=>AG&UeGATS^`F)lPVAYBS&Ze(v_Y6>$nATS_rVrmLJJPI#Vd2nSQFGX%+Z)9n1X9_PwX=Y|+a%FB~Wpf}~G&C<^G&CSIH7_o1Z**j3W*{^+FJUw`AT&2GE^cphWMyU`G&wI}G&vwOFfT4{Z**j3W*{~-FJU${AT~BHE^cphWMyU`H#RR}H#Q(QH!m)3Z**j3W*|5-FJU+{AUHHHE^cphWMyU`IX5q1IX5q1IXEw2IXN$3F)%PMVKFc<ATcm9FD`CxbYx{_ATcmAFJUn-GaxZAG%qf0Z**j3W*{*zH7{W?Ff}h>F)%hSVKFc_FJUn-I4@x_FgY(_F)=VNVKFf=FJUn;GB05<F*7e=F)=hRVKFf^FJUn;HZNf@F*h$^F)=tGF)=wWE^cphWMyU`F)}ePVKFi>T?#%v3T19&Z(?c+Gc_PEAa7!73OqatFJUw^AT}T{AW{l1VKg=%Hy|(|QVK6&G&vwMG9WM@QVK6&HZ>qPATS_O3NK+dHXu15Fd$M2FJU+{ATcl?Fd$M2FJU=1ATco@Fd$M2FJU=2ATcr^Fd$M2FJU=3ATcu_Fd$M2FJUn-Fd#8BATS_O3NK+XFfkx8H6Sn`QVK6&F)%YAF*YDDAW{l1VKFc@ATc)}Fd$M2FJUn-HXt!LATS_O3NK+XFgGAEIUq0~QVK6&F)%nFGB6-8AW{l1VKFc{ATlu^Fd$M2FJUn;Fd#BAATS_O3NK+XF)<)AGaxV^QVK6&F)=bAGBhACAW{l1VKFf?ATl)|Fd$M2FJUn;G$1lIATS_O3NK+XF*P7EHy|(|QVK6&F)=nEGB_YGAW{l1VKFf`ATl{1Fd$M2FJUn;I3P1HATS_O3NK+XGBF@CF(5D?QVKpk3T19&Z(?c+H6Sn`Z(?c+JUj|7RC#b^ATLm1XJvB=FGFv2Zge0q3NK4(WOE=}G9WM@Qe6r@J_==SWN%_>3Ntn!Fd%PYY6?6&3NKW7aAhDbLt%7bY;R`@FHm7;Wpf}kATS_O3O+sxWo~3|VrmLAHy|(|Z(?c+JUj|7P;zf%bz^06ASg{~OH^f8AaG=6RApE#F)lPPE-^PL3NJ%)Wnpx0av&&FWmqW+FGF%=VRUJ4ZbV^pWgsX-Ix;XaFfcbTGBGnTH!v|PFfu1FFefPrFHLV`L}7GgASgsSGB7eQFgGwVF*7kYFfl7IGAA%FCn*XqRB~Z(aAjm5FGgW(b7cxIP*g=&E=F~1Y+_+<Ze?;HC{$=^b0BGRAWdmYRApE#aAamwWmq6GE;%kXGBGhAC^0THFfK7SDJcp*J_==SWN%_>3V3p5W(qJMGdKz`FfcGMFfcGMFd#NHH8V9JW*`bMFfcGMFfcYaG$1fAFfcG6ZXgOUFfcGMFfcVZFd#56FfcG6ZXgOUFfcGMFfcGNH6SoBFfcG6ZXgOUFfcGMFgP$aIUq1FFfcG6ZXgOUFfcGMFgY?eG9WN8FfcG6ZXgOUFfcGMFfcbYG9WN8FfcG6ZXgOUFfcGMFfchbHy|)DFfcG6ZXgOUFfcGMFflPSF(5E7FfcG6ZXgOUFfcGMFflYYHy|)DFfcG6ZXgOUFfcGMFflhUI3O@EFfcG6ZXgOUFfcGMFfuSVHy|)DFfcG6ZXgOUFfcGMFfubZHXtxCFfcG6ZXgOUFfcGMFfukbIUq1FFfcG6ZXgOUFfcGMFfutdG9WN8FfcG6ZXgOUFfcGMFf%eWG$1fAFfcG6ZXgOUFfcGMFf%nYG$1fAFfcG6ZXgOUFfcGMFf%wgIUq1FFfcG6ZXgOUFfcGMFf=hRG$1fAFfcG6ZXgOUFfcGMFf=nXH6SoBFfcG6ZXgOUFfcGMFf=waH6SoBFfcG6ZXgOUFfcGMFf=$bH6SoBFfcG6ZXgOUFfcGMFf}nTI3O@EFfcG6ZXgOUFfcGMFf}tZHy|)DFfcG6ZXgOUFfcGMFf}$bHXtxCFfcG6ZXgOUFfcGMFf}<eG$1fAFfcG6ZXgOUFfcGMFg7wYIUq1FFfcG6ZXgOUFfcGMFg7$dGaxW9FfcG6ZXgOUFfcGMFg7<fHXtxCFfcG6ZXgOUFfcGMFgGwTHXtxCFfcG6ZXgOUFfcGMFgG$ZI3O@EFfcG6ZXgOUFfcGMFgG<bFd#56FfcG6ZXgOUFfcGMFgG|gI3O@EFfcG6ZXgOUFfcGMFgP<YH6SoBFfcG6ZXgOUFfcGMFgP_iI3O@EFfcG6ZXgOUFfcGMFgQ6eG9WN8FfcG6ZXgOUFfcGMFgY_aIUq1FFfcG6ZXgOUFfcGMFgY_fIUq1FFfcG6ZXgPDa$#v~WpWBUJRmPqX?kTKGdKz_Qg3f`ATu@~Fd$M2FG+4@Zy+-_ATS_O3NJ}SAX_{&Hbq1@I5;vwH#IOsHZeFvG(#{rI5$Q(H8(;xGB86vAUriTMMO9_I5I*vH84arF*rmtLohfvH%2%$H$pcuFhf3FAU-|{b97;Hba--QW(qkrFfj@xB}Gq03I"
    doc.save()

def getData():
    data = {
        "oai:arXiv.org:121518513": {
            "modified_at": 1625154502,
            "date": "2007-05-23",
            "year": "2007",
            "setSpec": "{'lor'}",
            "title": "Lorem ipsum dolor",
            "subject": "{'Lorem - Ipsum', '12O18'}",
            "abstract": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr. \nComment: 11 pages",
            "tags": ["lorem", "ipsum","dolor","sit","amet", "consetetur", "elitr", "sadipscing"],
            "abstract_offsets": [(0,56)],
            "meta_id": [
                "http://arxiv.org/abs/121518513"
            ]
        },
        "Lorem": {
            "modified_at": 1625154404,
            "title": "voluptua",
            "entrytype": "inproceedings",
            "year": "2019",
            "publisher": "Association for Lorem Ipsum",
            "cited_by": "test",
            "author": [
                "Lorem Ipsum",
                "Lörem Ipßüm",
                "Sadipscing Elitr"
            ],
            "editor": [
                "Lorem Ipsum",
                "Lörem Ipßüm",
                "Sadipscing Elitr"
            ]
        },
        "Ipsum2019a": {
            "modified_at": 1625154478,
            "entrytype": "inproceedings",
            "year": "2019",
            "publisher": "Association for Lorem Ipsum",
            "cited_by": "test",
            "author": [
                "Lorem Ipsum"
            ],
            "editor": [
                "Lorem Ipsum",
                "Lörem Ipßüm"
            ]
        },
        "121518513": {
            "modified_at": 1625154508,
            "title": "Lorem ipsum dolor",
            "date": "2020-02-02",
            "year": "2020",
            "author": [
                "Lorem Ipsum",
                "Lörem Ipßüm"
            ],
            "editor": [
                "Lörem Ipßüm"
            ],
            "doi": "121518513",
            "fulltext": "ABSTRACT\nLorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\nINTRODUCTION\nLorem ipsum.",
            "abstract": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.",
            "abstract_offsets": [(0,26),(28,55),(57,135),(137,154)],
            "tags": ["lorem", "ipsum","dolor","tempor","invidunt", "labore", "magna", "voluptua", "sadipscing", "aliquyam"]
        },
        "PMID121518513": {
            "modified_at": 1625154512,
            "PMID": "121518513",
            "Version": "1",
            "url": "https://www.ncbi.nlm.nih.gov/pubmed/121518513",
            "title": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr.",
            "abstract": "Lorem ipsum",
            "abstract_offsets": [(0,11)],
            "tags": ["lorem", "ipsum"],
            "editor": [
                "Lorem Ipsum",
                "Ipßüm Lörem"
            ],
            "volume": "25",
            "issue": "13",
            "year": "2018",
            "month": "march",
            "journal": "Lorem ipsum dolor",
            "mesh": [
                "Lorem, Ipsum",
                "Lorem, Ipsum, Dolor"
            ]
        },
        "miss": {
            "title": "Miss"
        }
    }
    return data

def main(elastic = False, doc = False, user = False, pdf = False):
    """
    Creates ArangoDB and Elasticsearch Data for all Flask tests
    Reset options are for use after changes here, not for resest while testing

    Parameters
    ----------
    elastic : bool, optional
        If true Elasticsearch Data will be resetted, by default False
    doc : bool, optional
        If true ArangoDB Document Data will be resetted, by default False
    user : bool, optional
        If true ArangoDB User Data will be resetted, by default False
    pdf : bool, optional
        If true ArangoDB PDF Data will be resetted, by default False
    """ 
    conn, db, allowed = setup()
    data = getData()

    name = config["index"]
    if not conn.indices.exists(index=name):
        print("Create Elasticsearch Data")
        setupElasticsearch(data, allowed)
    elif elastic:
        print("Reset Elasticsearch Data")
        conn.indices.delete(index=name)
        setupElasticsearch(data, allowed)
    
    name = config["documentcollection"]
    if not db.hasCollection(name):
        print("Create ArangoDB Document Data")
        collection = db.createCollection(name=name)
        setupArangoDBDocuments(collection, data)
    elif doc:
        print("Reset ArangoDB Document Data")
        collection = db[name]
        collection.empty()
        setupArangoDBDocuments(collection, data)
    
    name = config["usercollection"]
    if not db.hasCollection(name):
        print("Create ArangoDB User Data")
        collection = db.createCollection(name=name)
        setupArangoDBUser(collection)
    elif user:
        print("Reset ArangoDB User Data")
        collection = db[name]
        collection.empty()
        setupArangoDBUser(collection)
    
    name = config["pdfcollection"]
    if not db.hasCollection(name):
        print("Create ArangoDB PDF Data")
        collection = db.createCollection(name=name)
        setupArangoDBPDF(collection)
    elif pdf:
        print("Reset ArangoDB PDF Data")
        collection = db[name]
        collection.empty()
        setupArangoDBPDF(collection)

