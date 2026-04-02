# 加载必要的包
library(ggplot2)
library(viridis)  # 用于颜色渐变

# 读取数据
setwd("C:/Users/chenr/Desktop/Result_Influenza_pandemic/Mar27_2026/Output_dataset/")
data <- read.csv("cost_analysis_FCFS_R03_output_to_CEA_anti_n_vaccine_3month.csv")

# 查看数据结构
head(data)
str(data)


# 将比例转换为百分比
data$BXM_percent <- data$BXM_proportion * 100
data$OTV_percent <- data$OTV_proportion * 100

# 创建气泡热力图
ggplot(data, aes(x = BXM_percent, y = OTV_percent)) +
  #geom_point(aes(size = AR, color = RAR), alpha = 0.7) +
  geom_point(aes(size = AR, fill = RAR), shape = 21, color = "black", alpha = 0.7) +
  scale_size_continuous(
    name = "AR",
    range = c(4, 9),  # 调整气泡大小范围
    breaks = seq(min(data$AR), max(data$AR), length.out = 5),
    labels = function(x) sprintf("%.4f", x),
    guide = guide_legend(order = 1)  # AR图例在上方
  ) +
  #scale_color_viridis(
  scale_fill_viridis(
    name = "RAR",
    #option = "plasma",  # 可以选择 "viridis", "plasma", "inferno", "magma"
    option = "plasma",  # 可以选择 "viridis", "plasma", "inferno", "magma"
    direction = -1     # 反转颜色顺序，如果需要的话

  ) +
  labs(
    #title = "Bubble Heatmap With Vaccine",
    x = "Baloxavir Proportion (%)",
    y = "Oseltamivir Proportion (%)"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
    axis.title = element_text(size = 12),
    axis.text = element_text(size = 10),
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 8),
    panel.grid.major = element_line(color = "grey80", linewidth = 0.2),
    panel.grid.minor = element_blank(),
    aspect.ratio = 6/10  # 设置横纵比为10:6
  ) +
  # 添加数值标签（可选）
  #geom_text(aes(label = round(AR, 4)), size = 3, vjust = -1.5) +
  # 调整坐标轴范围
  scale_x_continuous(breaks = c(0, 20, 40, 60, 80, 100), limits = c(0, 100)) +
  scale_y_continuous(breaks = c(0, 20, 40, 60, 80, 100), limits = c(0, 100))

# 如果想要保存图片，取消注释下面这行

ggsave("FCFS_R03_bubble_heatmap_vaccine_diff.png", width = 8, height = 4.8, dpi = 300)

