# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 21:23:44 2025

@author: chenr
"""

import pandas as pd
import numpy as np

# Direct cost parameter
COST_PARAMS = {
    'Vaccine': 260,
    'Outpatient_consultation': 1500,
    'Test': 450,
    'Xofluza': 343,  # Baloxavir
    'Tamiflu': 30,   # Oseltamivir
    'Relenza': 200,  # Zanamivir
    'Inpatient': 5100,
    'ICU': 15350
}

# Indirect cost: Societal Perspective 
SOCIETAL_PARAMS = {
    'daily_wage': 1025,
    'annual_wage': 246000,
    'workdays_lost_per_case': 3,
    'hospital_stay_duration': 5,
    'icu_stay_duration': 10,
    'care_days_per_case': 2,
    'remaining_work_years_0_18': 47,
    'remaining_work_years_19_64': 23.4,
    'remaining_life_0_18': 77.75,
    'remaining_life_19_64': 45.98,
    'remaining_life_65': 11.66
}

# QALY parameter
QALY_PARAMS = {
    'TRAEs_antiviral_loss': 0.00378082191780822,
    'TRAEs_antiviral_rate': [0.056, 0.079, 0.0625],  
    'TRAEs_vaccine_rate': 0.043,
    'TRAEs_vaccine_loss': 0.00109589,
    'influenza_symp_loss': (2/3) * 0.000021689497716895, # 2/3 are sypmtomatic patient, 1/3 asypmtomatic no including.
    'influenza_duration': [53.5, 53.8, 68.2, 80.2], #BXM, OTV, ZNV, No treatment
    'complication_loss': (2/3) * 0.00522452830188679, 
    'complication_rate': [0.021, 0.047, 0.054, 0.048], #BXM, OTV, ZNV, No treatment
    'treatment_rate': [0.6, 0.4],  #  60% treatment rate
    'hospital_loss': 0.00712328767123288, 
    'icu_loss': 0.01643835616438356, #icu qaly loss per year:0.6
    'death_loss': 0.9344
}


#print(QALY_PARAMS['influenza_duration'][1])




def calculate_costs(df):
    """
    计算各项成本
    """
    results = []
    
    for _, row in df.iterrows():

        hospitalization_cost = row['Hospitalization'] * COST_PARAMS['Inpatient'] * SOCIETAL_PARAMS['hospital_stay_duration'] + (row['Death_0_18'] + row['Death_19_64'] +row['Death_65'])* COST_PARAMS['ICU'] * SOCIETAL_PARAMS['icu_stay_duration']
        
        outpatient_cost = row['cumulative_incidence_Total'] * (2/3) * (COST_PARAMS['Outpatient_consultation'] + COST_PARAMS['Test']) #2/3 sympton
        
        vaccine_cost = row['Vaccine_used'] * COST_PARAMS['Vaccine']
        
        drug_cost = row['Antiviral_used'] * (
            row['BXM_proportion'] * COST_PARAMS['Xofluza'] +
            row['OTV_proportion'] * COST_PARAMS['Tamiflu'] +
            row['ZNV_proportion'] * COST_PARAMS['Relenza']
        )
        
        # direct_cost_total
        direct_cost_total = hospitalization_cost + outpatient_cost + vaccine_cost + drug_cost
        
        productivity_loss = (
            row['incidence_19_64'] * SOCIETAL_PARAMS['workdays_lost_per_case'] * SOCIETAL_PARAMS['daily_wage'] +
            row['hos_19_64'] * SOCIETAL_PARAMS['hospital_stay_duration'] * SOCIETAL_PARAMS['daily_wage'] +
            row['Death_0_18'] * SOCIETAL_PARAMS['remaining_work_years_0_18'] * SOCIETAL_PARAMS['annual_wage'] +
            row['Death_19_64'] * SOCIETAL_PARAMS['remaining_work_years_19_64'] * SOCIETAL_PARAMS['annual_wage']
        )
        
        caregiver_burden = (
            row['incidence_0_18'] * SOCIETAL_PARAMS['care_days_per_case'] * SOCIETAL_PARAMS['daily_wage'] +
            row['Hospitalization'] * SOCIETAL_PARAMS['care_days_per_case'] * SOCIETAL_PARAMS['daily_wage']
        )
        
        indirect_cost_total = productivity_loss + caregiver_burden
        
        # Total cost
        total_cost = direct_cost_total + indirect_cost_total
        
        # QALY
        # TRAEs (治疗相关不良事件)
        TRAEs = (
            row['Antiviral_used'] * QALY_PARAMS['TRAEs_antiviral_loss'] * 
             (row['BXM_proportion']*QALY_PARAMS['TRAEs_antiviral_rate'][0] + 
              row['OTV_proportion']*QALY_PARAMS['TRAEs_antiviral_rate'][1] + 
              row['ZNV_proportion']*QALY_PARAMS['TRAEs_antiviral_rate'][2]) + 
            row['Vaccine_used'] * QALY_PARAMS['TRAEs_vaccine_rate'] * QALY_PARAMS['TRAEs_vaccine_loss']
        )
        
        # 流感症状

        influenza_symp = (
            row['cumulative_incidence_Total'] * QALY_PARAMS['influenza_symp_loss'] * 
            (QALY_PARAMS['treatment_rate'][0] * 
              (row['BXM_proportion']*QALY_PARAMS['influenza_duration'][0] + 
              row['OTV_proportion']*QALY_PARAMS['influenza_duration'][1] + 
              row['ZNV_proportion']*QALY_PARAMS['influenza_duration'][2]) + 
            QALY_PARAMS['treatment_rate'][1] * QALY_PARAMS['influenza_duration'][3])
        
        )
        
        # 并发症
        complication = (
            row['cumulative_incidence_Total'] * QALY_PARAMS['complication_loss'] *
            (QALY_PARAMS['treatment_rate'][0] * 
             (row['BXM_proportion']*QALY_PARAMS['complication_rate'][0] + 
             row['OTV_proportion']*QALY_PARAMS['complication_rate'][1] + 
             row['ZNV_proportion']*QALY_PARAMS['complication_rate'][2]) + 
            QALY_PARAMS['treatment_rate'][1] * QALY_PARAMS['complication_rate'][3])
        )
        
        # 住院
        hospital_qaly = row['Hospitalization'] * QALY_PARAMS['hospital_loss'] + (row['Death_0_18'] + row['Death_19_64'] +row['Death_65']) * QALY_PARAMS['icu_loss']
        
        # 死亡
        death_qaly = (
            row['Death_0_18'] * SOCIETAL_PARAMS['remaining_life_0_18'] +
            row['Death_19_64'] * SOCIETAL_PARAMS['remaining_life_19_64'] +
            row['Death_65'] * SOCIETAL_PARAMS['remaining_life_65']
        ) * QALY_PARAMS['death_loss']
        
        # 总QALY
        total_qaly = TRAEs + influenza_symp + complication + hospital_qaly + death_qaly
        
        results.append({
            'Direct_cost_Hospitalization': hospitalization_cost,
            'Direct_cost_GP_Consultation_Test_Antiviral': outpatient_cost+vaccine_cost+drug_cost,
            'Direct_cost_Total': direct_cost_total,
            'Indirect_cost': indirect_cost_total,
            'Total_cost': total_cost,
            'Total_QALY': total_qaly
        })
    
    return pd.DataFrame(results)

# 使用示例
if __name__ == "__main__":
    # 读取数据（这里用您提供的数据作为示例）
    
    
    data = pd.read_csv('C:/Users/chenr/Desktop/Result_Influenza_pandemic/Mar27_2026/Output_dataset/FCFS_R03_output_to_CEA_anti_n_vaccine_3month.csv')
    
    df = pd.DataFrame(data)
    
    # 计算成本
    cost_results = calculate_costs(df)
    
    # 合并原数据和计算结果
    final_results = pd.concat([df, cost_results], axis=1)
    
    # 显示结果
    print(final_results)
    
    # 保存到文件
    final_results.to_csv('C:/Users/chenr/Desktop/Result_Influenza_pandemic/Mar27_2026/Output_dataset/cost_analysis_FCFS_R03_output_to_CEA_anti_n_vaccine_3month.csv', index=False)
