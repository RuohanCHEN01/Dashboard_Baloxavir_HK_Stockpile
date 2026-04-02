# 加载必要的包
library(ggplot2)
library(dplyr)
library(stringr)
library(viridis)
# 创建示例数据（请用您的实际数据替换）
setwd("C:/Users/chenr/Desktop/Result_Influenza_pandemic/Mar27_2026/Output_dataset/")
data <- read.csv("cost_analysis_FCFS_R03_output_to_CEA_anti_n_vaccine_3month.csv")

# 数据预处理
# 1. 清理INMB列：移除逗号和空格，转换为数值

data_clean <- data %>%
  mutate(
    inmb = str_replace_all(inmb, ",| ", ""),  # 移除逗号和空格
    inmb = as.numeric(inmb)  # 转换为数值
  ) %>%
  filter(!is.na(inmb))  # 移除缺失值

data_clean$OTV_proportion


# 创建基线数据点
baseline_point <- data.frame(
  BXM_proportion = 0,
  OTV_proportion = 0.9,
  inmb = 0
)
# 创建热力图 - 使用viridis颜色方案
heatmap_plot <- ggplot(data_clean, aes(x = BXM_proportion * 100, y = OTV_proportion * 100, fill = inmb)) +
  geom_tile(color = "black", size = 0.2) +
  # 使用viridis颜色方案
 

  scale_fill_viridis(
    name = "INMB",
    option = "viridis",  
    #na.value = "grey50",
    direction = -1   
  ) +

  # 使用viridis的双色渐变版本
  # 使用viridis的双色渐变版本（负值到正值对比更明显）
  # 使用viridis的两种不同方案创建双色渐变
  # 自定义颜色范围，确保对比更明显
#  scale_fill_gradient2(
#    name = "INMB",
#    low = "#440154",    # viridis深紫色
#    mid = "white",      # 白色
#    high = "#FDE725",   # viridis亮黄色
#    midpoint = 0,
#    na.value = "grey50"
#  ) +
  # 添加基线点 (0.9OTV + 0.1ZNV)
  geom_point(
    data = baseline_point,
    aes(x = BXM_proportion * 100, y = OTV_proportion * 100),
    color = "red",
    size = 4,
    shape = 18,
    show.legend = FALSE,
    inherit.aes = FALSE
  ) +
  geom_text(
    data = baseline_point,
    aes(x = BXM_proportion * 100, y = OTV_proportion * 100, label = "Baseline\n(90% OTV+\n10% ZNV)"),
    color = "red",
    size = 4,
    nudge_y = -13,
    nudge_x = 5,
    inherit.aes = FALSE
  ) +
  labs(
    #title = "Heatmap Without Vaccine",
    x = "Baloxavir Proportion (%)",
    y = "Oseltamivir Proportion (%)",
    fill = "INMB"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
    axis.title = element_text(size = 12),
    axis.text = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 8),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    legend.position = "right",
    aspect.ratio = 6/10 
  ) +
  # 修改横轴刻度为0,20,40,60,80,100，不显示%符号
  scale_x_continuous(
    breaks = c(0, 20, 40, 60, 80, 100),
    labels = c("0", "20", "40", "60", "80", "100")
  ) +
  # 修改纵轴与横轴一致
  scale_y_continuous(
    breaks = c(0, 20, 40, 60, 80, 100),
    labels = c("0", "20", "40", "60", "80", "100")
  )

# 显示图形
print(heatmap_plot)

# 可选：保存图形
ggsave("FCFS_R03_INMB_heatmap_novaccine_diff.png", plot = heatmap_plot, width = 8, height = 4.8, dpi = 300)
