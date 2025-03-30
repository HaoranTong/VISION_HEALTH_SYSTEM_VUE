import pandas as pd
import os


def check_and_preprocess_file(file_path):
    try:
        # 读取文件（根据文件类型选择不同的读取方式）
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            raise ValueError("不支持的文件格式，必须是 .xlsx 或 .csv")

        # 1. 检查列数一致性
        if len(df.columns) == 0:
            raise ValueError("文件没有列标题")

        for index, row in df.iterrows():
            if len(row) != len(df.columns):
                print(f"警告：第 {index + 1} 行列数与表头不一致！")

        # 2. 检查缺失值
        missing_values = df.isnull().sum()
        if missing_values.any():
            print("警告：以下列包含缺失值：")
            print(missing_values[missing_values > 0])

        # 3. 检查数据类型一致性
        print("检查数据类型：")
        print(df.dtypes)

        # 4. 检查日期列格式
        if 'birthday' in df.columns:
            df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce')
            if df['birthday'].isnull().any():
                print("警告：'birthday' 列包含无效的日期格式")

        # 5. 检查数值列格式（假设有数字列，比如视力数据、体重等）
        numeric_columns = ['height', 'weight',
                           'right_eye_naked', 'left_eye_naked']
        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors='coerce')
                if df[column].isnull().any():
                    print(f"警告：'{column}' 列包含无效的数值")

        # 6. 检查重复数据
        duplicates = df[df.duplicated()]
        if not duplicates.empty:
            print("警告：以下行数据是重复的：")
            print(duplicates)

        # 7. 检查是否有异常字符（例如特殊符号、空格等）
        for column in df.columns:
            if df[column].dtype == 'object':
                contains_special_chars = df[column].str.contains(
                    '[^\x00-\x7F]+', regex=True, na=False)
                if contains_special_chars.any():
                    print(f"警告：'{column}' 列包含非标准字符")

        # 8. 确保表头一致性
        expected_columns = ['education_id', 'school', 'class_name',
                            'name', 'gender', 'birthday', 'phone', 'id_card']
        missing_columns = set(expected_columns) - set(df.columns)
        if missing_columns:
            print(f"警告：缺少以下列：{missing_columns}")

        # 如果有任何检查失败，可以根据需求停止执行
        print("文件检查完成，无重大错误。")

        # 返回处理后的 DataFrame（可以继续进行后续处理或导入）
        return df

    except Exception as e:
        print(f"错误：{e}")
        return None


# 运行检查与预处理
file_path = 'your_file.xlsx'  # 替换为实际文件路径
processed_data = check_and_preprocess_file(file_path)

# 如果没有严重错误，可以继续后续处理
if processed_data is not None:
    # 继续进行后续的文件导入或数据处理
    print("数据已通过检查，可以进行后续处理。")


if __name__ == '__main__':
   # df = check_and_preprocess_file("suninghongjunxiaoxuebiaozhunshuju.xlsx")
    # 如果需要，可以进一步处理返回的 DataFrame

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        current_dir, "suninghongjunxiaoxuebiaozhunshuju.xlsx")
    df = check_and_preprocess_file(file_path)
