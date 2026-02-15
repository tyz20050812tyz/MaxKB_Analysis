import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

# 全局样式与字体设置 
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font=plt.rcParams['font.sans-serif'][0]) 

def generate_visualizations():
    print("正在生成高分辨率数据可视化图表...")
    os.makedirs('results/visuals', exist_ok=True)

    # --- 1. 代码异味分布图 ---
    smells_path = 'results/code_smells.json'
    if os.path.exists(smells_path):
        with open(smells_path, 'r', encoding='utf-8') as f:
            smells_data = json.load(f)
        if smells_data:
            df_smells = pd.DataFrame(smells_data)
            plt.figure(figsize=(10, 6), dpi=300)
            ax = sns.countplot(
                data=df_smells, x='issue', hue='severity', hue_order=['High', 'Medium', 'Low'],
                palette={'High': '#e74c3c', 'Medium': '#f39c12', 'Low': '#3498db'}
            )
            plt.title('MaxKB 代码异味分布情况', fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('异味类型', fontsize=12)
            plt.ylabel('发现数量', fontsize=12)
            plt.xticks(rotation=15)
            for p in ax.patches:
                height = p.get_height()
                if height > 0: 
                    ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height), 
                                ha='center', va='bottom', fontsize=10, xytext=(0, 4), textcoords='offset points')
            sns.despine(top=True, right=True)
            plt.legend(title='严重程度', alignment='left')
            plt.tight_layout()
            plt.savefig('results/visuals/smell_distribution.png', bbox_inches='tight')
            plt.close()
            print("  - 已生成: 高清异味分布图 (smell_distribution.png)")

    # --- 2. 核心模块复杂度热力图 ---
    complexity_path = 'results/complexity_report.json'
    if os.path.exists(complexity_path):
        with open(complexity_path, 'r', encoding='utf-8') as f:
            comp_data = json.load(f)
        if comp_data:
            df_comp = pd.DataFrame(comp_data)
            df_comp = df_comp[~df_comp['module'].str.contains(r'^[0-9]{4}_|migrations', regex=True)]
            module_complexity = df_comp.groupby('module')['complexity'].sum().reset_index()
            top_15 = module_complexity.sort_values(by='complexity', ascending=False).head(15)
            heatmap_matrix = top_15.set_index('module')[['complexity']]
            
            plt.figure(figsize=(8, 10), dpi=300)
            ax = sns.heatmap(heatmap_matrix, cmap='rocket_r', annot=True, fmt='d', linewidths=1.5, linecolor='white')
            plt.title('MaxKB 核心模块总复杂度排名 (Top 15)', fontsize=16, fontweight='bold', pad=20)
            plt.ylabel('业务模块名称', fontsize=12, labelpad=10)
            plt.xlabel('')
            plt.yticks(rotation=0, fontsize=11)
            plt.tight_layout()
            plt.savefig('results/visuals/complexity_heatmap.png', bbox_inches='tight')
            plt.close()
            print("  - 已生成: 高清复杂度热力图 (complexity_heatmap.png)")

    # --- 3. 安全漏洞分析图 (基于 Bandit 报告) ---
    security_path = 'results/security_issues.json'
    if os.path.exists(security_path):
        with open(security_path, 'r', encoding='utf-8') as f:
            try:
                sec_data = json.load(f)
                # Bandit 输出的 JSON 通常将漏洞详情放在 "results" 键中
                issues = sec_data.get('results', [])
                if issues:
                    df_sec = pd.DataFrame(issues)

                    # 高频安全漏洞类型 Top 5 (条形图)
                    plt.figure(figsize=(10, 6), dpi=300)
                    top_issues = df_sec['test_name'].value_counts().head(5)
                    
                    ax = sns.barplot(x=top_issues.values, y=top_issues.index, hue=top_issues.index, palette='Reds_r', legend=False)
                    plt.title('高频安全风险类型 Top 5', fontsize=16, fontweight='bold', pad=20)
                    plt.xlabel('触发次数 (次)', fontsize=12)
                    plt.ylabel('漏洞检测项 (Test Name)', fontsize=12)
                    
                    # 在柱状图右侧添加数据标签
                    for p in ax.patches:
                        ax.annotate(f'{int(p.get_width())}', 
                                    (p.get_width(), p.get_y() + p.get_height() / 2.), 
                                    ha='left', va='center', fontsize=11, xytext=(5, 0), 
                                    textcoords='offset points', fontweight='bold')
                        
                    sns.despine(right=True, top=True)
                    plt.tight_layout()
                    plt.savefig('results/visuals/security_top_issues.png', bbox_inches='tight')
                    plt.close()
                    print("  - 已生成: 高频漏洞类型条形图 (security_top_issues.png)")
                else:
                    print("  - 安全报告中未发现任何漏洞级别的内容。")
            except Exception as e:
                print(f"  - 解析安全报告失败: {e}")

if __name__ == "__main__":
    generate_visualizations()