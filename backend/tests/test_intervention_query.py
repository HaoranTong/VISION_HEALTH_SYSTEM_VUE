from sqlalchemy import create_engine, Column, Integer, String, Boolean, case, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from itertools import combinations
from sqlalchemy import and_, literal

# 创建数据库和模型
Base = declarative_base()


class Intervention(Base):
    __tablename__ = 'intervention'
    id = Column(Integer, primary_key=True)
    guasha = Column(Boolean, default=False)
    aigiu = Column(Boolean, default=False)
    zhongyao_xunzheng = Column(Boolean, default=False)
    rejiu_training = Column(Boolean, default=False)
    xuewei_tiefu = Column(Boolean, default=False)
    reci_pulse = Column(Boolean, default=False)
    baoguan = Column(Boolean, default=False)


# 创建 SQLite 内存数据库和表
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 模拟数据插入
interventions_data = [
    {'guasha': True, 'aigiu': False, 'zhongyao_xunzheng': False},
    {'guasha': False, 'aigiu': True, 'zhongyao_xunzheng': False},
    {'guasha': False, 'aigiu': False, 'zhongyao_xunzheng': True},
    {'guasha': True, 'aigiu': True, 'zhongyao_xunzheng': False},
    {'guasha': True, 'aigiu': False, 'zhongyao_xunzheng': True},
    {'guasha': False, 'aigiu': True, 'zhongyao_xunzheng': True},
    {'guasha': True, 'aigiu': True, 'zhongyao_xunzheng': True}
]

# 插入数据到数据库
for data in interventions_data:
    intervention = Intervention(**data)
    session.add(intervention)
session.commit()

# 创建 FIELD_LABEL_MAPPING 模拟字段映射
FIELD_LABEL_MAPPING = {
    "刮痧": "guasha",
    "艾灸": "aigiu",
    "中药熏蒸": "zhongyao_xunzheng",
    "热灸训练": "rejiu_training",
    "穴位贴敷": "xuewei_tiefu",
    "热磁脉冲": "reci_pulse",
    "拔罐": "baoguan",
}


def test_intervention_query(selected_interventions):
    conditions = []
    label_names = [FIELD_LABEL_MAPPING.get(
        f, f) for f in selected_interventions]

    # 单项干预措施的统计
    for f in selected_interventions:
        db_field = FIELD_LABEL_MAPPING.get(f, f)
        print(f"\nGenerating condition for single intervention: {f}")

        # 当前干预为True，其他为False
        other_conditions = [getattr(Intervention, FIELD_LABEL_MAPPING.get(other_f, other_f)) == False
                            for other_f in selected_interventions if other_f != f]
        exclusive_cond = and_(getattr(Intervention, db_field)
                              == True, *other_conditions)
        conditions.append(exclusive_cond)
        print(f"Condition: {exclusive_cond}")

    # 组合干预措施
    for r in range(2, len(selected_interventions)+1):
        for comb in combinations(selected_interventions, r):
            print(f"\nGenerating condition for combination: {comb}")
            combo_cond = and_(
                *[getattr(Intervention, FIELD_LABEL_MAPPING.get(f, f)) == True for f in comb])
            # 确保不包含其他选中的干预措施
            other_conditions = [getattr(Intervention, FIELD_LABEL_MAPPING.get(f, f)) == False
                                for f in selected_interventions if f not in comb]
            full_cond = and_(combo_cond, *other_conditions)
            conditions.append(full_cond)
            print(f"Condition: {full_cond}")

    # 使用OR连接所有条件
    query = session.query(Intervention)
    if conditions:
        query_conditions = or_(*conditions)
        query = query.filter(query_conditions)

    return query.all()


if __name__ == "__main__":
    # 测试查询，选择了 "刮痧" 和 "艾灸"
    print("=== 开始测试干预查询 ===")
    selected_interventions = ["刮痧", "艾灸"]
    result = test_intervention_query(selected_interventions)

    print("\n=== 查询结果 ===")
    for intervention in result:
        print(f"ID: {intervention.id}, 刮痧: {intervention.guasha}, 艾灸: {intervention.aigiu}, 中药熏蒸: {intervention.zhongyao_xunzheng}")

    print("\n=== 数据库中所有数据 ===")
    all_data = session.query(Intervention).all()
    for data in all_data:
        print(
            f"ID: {data.id}, 刮痧: {data.guasha}, 艾灸: {data.aigiu}, 中药熏蒸: {data.zhongyao_xunzheng}")
