#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import xlrd

def rulebasedProbablisticReasoner(pathModel, modelFileName, matchedRules, rupCases, unRupCases):
    '''
    @Author:                      MAQBOOL HUSSAIN
    @Created:                     Oct-19-2019
    @Last Updated:                Oct-23-2019
    @Last UpdateRemarks:
      i)
      
    @parameters:
        pathModel: The working directory of the probablistic model
        modelFileName: The file name where probabilistic model is saved.
        matchedRules: The rules matched. Provide as comma separated string values. Example string for three rules: R0,R2,R12
        rupCases: All cases which represent the intended class of study. [Format: a string of cases-ids separated with comma]
                  Here rupCases provide all rupture cases used in model for particular location.
        unRupCases: All other cases which is other than intended class. [Format: a string of cases-ids separated with comma]
                  Here the unruputred cases used in model for particular location is required.
    
    '''
    
    #Loading the rule matrix file
    model = pathModel+modelFileName
    df_rule_matrix=pd.read_excel( model )  #'ACOA_Rule_Matrix_1358.xlsx' for ACOM)
    df_rule_matrix.set_index('Rule#', inplace=True)
    
    rupCasesSet = set(int(x.strip()) for x in rupCases.split(','))
    unRupCasesSet = set(int(x.strip()) for x in unRupCases.split(','))
    
    ruleCobmineCases = set()
    rulesEvaluationMatrix=[]    

    for rule in matchedRules.split(','):
        mCases = df_rule_matrix.loc[int(rule[1:])]['Matched_Case'][1:len(df_rule_matrix.loc[int(rule[1:])]['Matched_Case'])-1]  # Get a matched cases as a string by removing [ and ]
        mCasesSet = set(int(x.strip()) for x in mCases.split(','))  # Conversion of matched cases string into a set
        ruleCobmineCases = ruleCobmineCases | mCasesSet # take a union of 2 sets           
        
#    set diff
    ruleComRupCases = len(ruleCobmineCases - unRupCasesSet)
    ruleComUnRupCases = len(ruleCobmineCases - rupCasesSet)
    
    rulesRupRiskProbability = ruleComRupCases/(len(unRupCasesSet)+len(rupCasesSet))
    rulesPrecision = ruleComRupCases/len(ruleCobmineCases)
    rulesRecall = ruleComRupCases/len(rupCasesSet)
     
    rulesEvaluationMatrix.append(('Rupture Risk Probability', rulesRupRiskProbability))
    rulesEvaluationMatrix.append(('Precision', rulesPrecision))
    rulesEvaluationMatrix.append(('Recall', rulesRecall))
    
    return rulesEvaluationMatrix     
    
#Calling the Reasoner method
'''
rulebasedProbablisticReasoner(pathModel, modelFileName, matchedRules, rupCases, unRupCases):

'''

# Uncomment following three statments and comment others if using PCOM
rupCasesPCOM = '495,523,389,1592,455,54,687,398,368,427,749,640,322,431,738,2048,1351,1471,1933,123,901,1476,605,652,720,1015,111,306,400,1884,417,1148,1985,20,955,1397,868,1078,1540,337,670,472,2007,80,892,1734,551,756,348,692,737,967,1335,1539,1997,476,1325,1473,1026,464,563,370,1503,420,654,732,1591,87,719,2050,35,1976,411,748,422,1558,1077'
unRupCasesPCOM = '270,129,1142,789,608,177,494,1427,1606,208,405,1145,354,520,694,897,820,83,209,1219,1443,1610,474,851,906,1056,1550,112,250,399,651,986,136,246,226,957,828,1241,2022,2046,829,138,200,1172,39,919,1126,140,568,223,14,1319'

#Three statments
rupCases = rupCasesPCOM
unRupCases = unRupCasesPCOM
modelFileName='PCOM_Rule_Matrix_PCOM_20191005.xlsx'

# Uncomment following three statments and comment others if using MCA (all available cases)
unRupCasesMCA = {2042,918,2057,663,8,211,435,641,23,1544,1626,342,655,1553,598,638,909,1095,680,1586,1589,1035,1076,1448,1556,113,362,560,639,1220,122,894,1457,1522,227,375,606,1557,1563,577,1023,1627,164,498,599,1032,1127,1543,1588,324,673,187,459,677,1587,406,1041,2031,401,1301,831,1546,297,521,1440,2002,61,914,1296,1354,31,107,1396,206,382,1226,1418,1420,1573,618,997,1116,452,782,1014,1144,221,1470,1528,179,1605,85,1559,159,852,1551,1936,74,876,2027,1295,1312,198,196,371,931,1393,1311,1595,28,1630,1043,147,2061}
rupCasesMCA = {962,213,1555,1487,746,1579,1583,280,1042,1123,1577,696,338,497,1019,1239,278,658,1545,102,22,377,569,725,77,765,602,91,72,193,1432,203,1523,1552,1889,1998,236,1601,1348,104,169,350,529,590,524,1106}
#Three statments
# rupCases = rupCasesMCA
# unRupCases = unRupCasesMCA
# modelFileName='MCA_Rule_Matrix_MCA_20190927.xlsx'

# Uncomment following two statments and comment others if using ACOM
rupCasesACOM = {1307,202,845,932,437,870,581,197,1529,245,268,733,936,1496,1514,1533,1541,330,739,1037,1055,151,174,249,261,1891,266,496,503,1170,1561,1603,192,702,724,1410,705,1255,265,428,1111,1121,513,1114,1195,1417,2030,712,752,230,1285,2062,195,519,713,774,366,619,1982,682,1566,1570,286,715,1147,701,865,920,1531,57,199,1512,217,656,785,1532,1009,1521,182,426,1036,2053,1231,1565,2032,913,1006,1181,1395,346,860,1402,163,7,1594}
unRupCasesACOM ={1458,1040,629,535,710,745,1064,282,633,714,344,536,592,731,1344,709,281,320,751,770,75,84,395,614,1361,2052,293,314,686,970,1090,445,1112,1486,384,385,392,659,736,298,564,604,695,108,285,296,465,700,1490,124,308,475,480,667,690,698,1066,448,743,44,89,541,881,1419,959,1358,1530,425,726,907,990,1562,866,867,1159,155,555,1080,95,489,591,660,1070,1370,1596,1599,424,1542,387,684,703,1995,341,668,351,378,594,706,1065,711,1983,135,1735,207,1524,329,622,1501,1357,1580,1602,58,319,854,1353,73,432,1139,132,1459,984,40,446,168,2016,804,71,343,490,634,1977,2008,1981,62}

# rupCases = rupCasesACOM
# unRupCases = unRupCasesACOM
# modelFileName='ACOA_Rule_Matrix_1358.xlsx'


# PASS FROM API SERVICE
matchedRulesMCA ='R1,R4,R5,R6,R8,R10,R17,R18,R19,R22,R23,R24,R25,R26,R28,R29,R30,R31,R34'
#matchedRulesMCA='R0,R1,R2,R3,R4,R6,R7,R8,R11,R12,R13,R14,R15,R21,R24,R27,R31'

matchedRules=matchedRulesMCA
pathModel='assets/'  #specify the location of the model file if not located at same folder of executable code

#Calling the reasoner and displaying the results
evalResult = rulebasedProbablisticReasoner(pathModel, modelFileName, matchedRules, rupCases, unRupCases)

print (evalResult)
 



