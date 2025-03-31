import pandas as pd

df = pd.read_excel(
    r"C:\Users\Haora\Desktop\04-曲线社区信息化项目\耳穴压丸项目\耳穴圧丸数据统计及标准化导入\华兴小学格式标准格式数据-测试修改.xlsx")
for col in df.columns:
    print(repr(col))
