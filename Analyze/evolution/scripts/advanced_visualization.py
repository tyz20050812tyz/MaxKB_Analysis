#!/usr/bin/env python3
"""
高级可视化分析脚本
生成丰富的图表和3D可视化效果
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class AdvancedVisualizer:
    def __init__(self, data_file='data/all_commits.json'):
        """初始化可视化器"""
        print("📊 初始化高级可视化分析器...")
        self.load_data(data_file)
        self.prepare_data()
        
    def load_data(self, file_path):
        """加载数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        print(f"✓ 加载数据: {len(self.raw_data)} 条记录")
        
    def prepare_data(self):
        """准备分析数据"""
        # 转换为DataFrame
        self.df = pd.DataFrame(self.raw_data)
        self.df['date'] = pd.to_datetime(self.df['date'])
        
        # 提取代码变更数据
        self.df['insertions'] = self.df['stats'].apply(lambda x: x.get('additions', 0))
        self.df['deletions'] = self.df['stats'].apply(lambda x: x.get('deletions', 0))
        self.df['net_change'] = self.df['insertions'] - self.df['deletions']
        
        # 按作者聚合
        self.author_stats = self.df.groupby('author').agg({
            'hash': 'count',
            'insertions': 'sum',
            'deletions': 'sum',
            'date': ['min', 'max']
        }).round(2)
        
        self.author_stats.columns = ['commits', 'insertions', 'deletions', 'first_commit', 'last_commit']
        self.author_stats['net_code'] = self.author_stats['insertions'] - self.author_stats['deletions']
        self.author_stats = self.author_stats.sort_values('commits', ascending=False)
        
        print("✓ 数据准备完成")
        
    def create_3d_contributor_landscape(self):
        """创建3D贡献者景观图"""
        print("🎨 生成3D贡献者景观图...")
        
        top_authors = self.author_stats.head(20)
        
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # 3D散点图：X=提交数, Y=净代码变更, Z=贡献时长
        x = top_authors['commits']
        y = top_authors['net_code']
        z = (top_authors['last_commit'] - top_authors['first_commit']).dt.days
        
        # 颜色映射（按提交数）
        colors = plt.cm.viridis(np.linspace(0, 1, len(top_authors)))
        
        scatter = ax.scatter(x, y, z, c=colors, s=100, alpha=0.8, edgecolors='black')
        
        ax.set_xlabel('提交数量', fontsize=12, labelpad=10)
        ax.set_ylabel('净代码变更 (行)', fontsize=12, labelpad=10)
        ax.set_zlabel('贡献时长 (天)', fontsize=12, labelpad=10)
        ax.set_title('3D 贡献者景观图\n(Top 20 贡献者)', fontsize=14, pad=20)
        
        # 添加标签
        for i, (author, row) in enumerate(top_authors.iterrows()):
            if i < 8:  # 只标记前8名避免拥挤
                ax.text(row['commits'], row['net_code'], 
                       (row['last_commit'] - row['first_commit']).days,
                       author.split()[0], fontsize=8)
        
        plt.tight_layout()
        plt.savefig('results/3d_contributor_landscape.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_3d_contributor_network(self):
        """创建3D贡献者网络图 (PNG格式)"""
        print("🌐 生成3D贡献者网络图...")
        
        # 准备网络数据
        authors = self.author_stats.head(15).index.tolist()
        commits = self.author_stats.head(15)['commits'].tolist()
        
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # 3D散点图
        x = commits
        y = [np.log(c) for c in commits]
        z = list(range(len(authors)))
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(authors)))
        scatter = ax.scatter(x, y, z, c=colors, s=[max(100, c*5) for c in commits], 
                           alpha=0.8, edgecolors='black')
        
        # 添加标签
        for i, author in enumerate(authors):
            if i < 8:
                ax.text(x[i], y[i], z[i], author.split()[0], fontsize=9)
        
        ax.set_xlabel('提交数量', fontsize=12)
        ax.set_ylabel('Log(提交数量)', fontsize=12)
        ax.set_zlabel('贡献者排名', fontsize=12)
        ax.set_title('3D 贡献者网络图 (Top 15)', fontsize=14, pad=20)
        
        plt.tight_layout()
        plt.savefig('results/3d_contributor_network.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_time_series_heatmap(self):
        """创建时间序列热力图"""
        print("🌡️ 生成时间序列热力图...")
        
        # 按周聚合数据
        self.df['week'] = self.df['date'].dt.isocalendar().week
        self.df['year'] = self.df['date'].dt.year
        
        weekly_data = self.df.groupby(['year', 'week']).agg({
            'hash': 'count',
            'author': 'nunique'
        }).reset_index()
        
        # 创建透视表
        pivot_commits = weekly_data.pivot(index='week', columns='year', values='hash').fillna(0)
        pivot_authors = weekly_data.pivot(index='week', columns='year', values='author').fillna(0)
        
        # 绘制热力图
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        sns.heatmap(pivot_commits, ax=axes[0], cmap='YlOrRd', cbar_kws={'label': '每周提交数'})
        axes[0].set_title('每周提交活动热力图')
        axes[0].set_xlabel('年份')
        axes[0].set_ylabel('周数')
        
        sns.heatmap(pivot_authors, ax=axes[1], cmap='Blues', cbar_kws={'label': '每周活跃贡献者数'})
        axes[1].set_title('每周活跃贡献者热力图')
        axes[1].set_xlabel('年份')
        axes[1].set_ylabel('周数')
        
        plt.tight_layout()
        plt.savefig('results/activity_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_pareto_analysis_3d(self):
        """创建3D帕累托分析图"""
        print("📊 生成3D帕累托分析图...")
        
        # 计算累积百分比
        sorted_commits = self.author_stats['commits'].sort_values(ascending=False)
        cumulative_pct = (sorted_commits.cumsum() / sorted_commits.sum()) * 100
        author_positions = range(1, len(sorted_commits) + 1)
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 3D柱状图
        ax.bar3d(author_positions, [0]*len(author_positions), [0]*len(author_positions),
                dx=0.8, dy=0.8, dz=sorted_commits.values, 
                color=plt.cm.plasma(np.linspace(0, 1, len(sorted_commits))))
        
        # 添加累积曲线
        ax.plot(author_positions, [100]*len(author_positions), cumulative_pct.values, 
               color='red', linewidth=3, label='累积百分比')
        
        ax.set_xlabel('贡献者排名')
        ax.set_ylabel('最大值参考')
        ax.set_zlabel('提交数量')
        ax.set_title('3D 帕累托分析图')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig('results/3d_pareto_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_code_churn_analysis(self):
        """创建代码变更分析图 (PNG格式)"""
        print("🔄 生成代码变更分析图...")
        
        # 按月聚合代码变更
        self.df['month'] = self.df['date'].dt.to_period('M')
        monthly_code = self.df.groupby('month').agg({
            'insertions': 'sum',
            'deletions': 'sum'
        }).reset_index()
        
        monthly_code['month'] = monthly_code['month'].astype(str)
        
        # 创建堆叠柱状图
        fig, ax = plt.subplots(figsize=(15, 8))
        
        bars1 = ax.bar(monthly_code['month'], monthly_code['insertions'], 
                      label='代码新增', color='green', alpha=0.7)
        bars2 = ax.bar(monthly_code['month'], -monthly_code['deletions'], 
                      label='代码删除', color='red', alpha=0.7)
        
        ax.set_xlabel('月份', fontsize=12)
        ax.set_ylabel('代码行数', fontsize=12)
        ax.set_title('月度代码变更分析', fontsize=14, pad=20)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签避免重叠
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig('results/code_churn_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def create_contributor_diversity_wheel(self):
        """创建贡献者多样性轮图"""
        print("🎯 生成贡献者多样性轮图...")
        
        # 计算贡献分布
        total_commits = self.author_stats['commits'].sum()
        top_5 = self.author_stats.head(5)['commits'].sum() / total_commits * 100
        next_15 = self.author_stats.iloc[5:20]['commits'].sum() / total_commits * 100
        others = 100 - top_5 - next_15
        
        labels = ['Top 5 贡献者', '第6-20名贡献者', '其他贡献者']
        values = [top_5, next_15, others]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=14
        )])
        
        fig.update_layout(
            title="贡献者多样性分布",
            width=600,
            height=600
        )
        
        fig.write_html('results/contributor_diversity.html')
        
    def generate_all_visualizations(self):
        """生成所有可视化图表"""
        print("=" * 60)
        print("🎨 开始生成高级可视化图表")
        print("=" * 60)
        
        # 创建输出目录
        import os
        os.makedirs('results', exist_ok=True)
        
        # 生成各种图表
        self.create_3d_contributor_landscape()
        self.create_interactive_contributor_network()
        self.create_time_series_heatmap()
        self.create_pareto_analysis_3d()
        self.create_code_churn_analysis()
        self.create_contributor_diversity_wheel()
        
        print("\n✅ 所有可视化图表生成完成！")
        print("\n📁 输出文件:")
        print("  • results/3d_contributor_landscape.png")
        print("  • results/interactive_contributor_network.html")
        print("  • results/activity_heatmap.png")
        print("  • results/3d_pareto_analysis.png")
        print("  • results/code_churn_analysis.html")
        print("  • results/contributor_diversity.html")

def main():
    """主函数"""
    visualizer = AdvancedVisualizer()
    visualizer.generate_all_visualizations()

if __name__ == '__main__':
    main()