### 第一期建模目标
1. 使用最简单的人物模型和关系模型，在随机初始化的关系网络上实现网络发展。
1. 选择的实现框架应有以下特征：
   * 人物模型和关系模型易于维护和扩展
   * 发展规律易于编写和维护
   * 可视化发展规律
1. 解决方案：
   * 编程语言：python3.6
   * 数据存储和查询：Neo4j+[python-driver](https://neo4j.com/developer/python/)+[cypher](https://neo4j.com/docs/cypher-refcard/current/)
   * 数据可视化：[以javascript为语言的诸多可视化工具](https://neo4j.com/developer/guide-data-visualization/)

### 细节问题
1. 固定使用的各种环境版本 or 在一个docker环境上面编程 or 租用一个共享服务器
   * 目前我有一台做VPS的机器：1核、500M内存、10G硬盘，可以进行初步测试使用。
   * 或者在这个代码仓库里维护一个创建docker文件的文件？
1. 模型的创建、维护和扩展：
   * neo4j支持给节点增加任意数量kv形式的属性
   * neo4j支持给节点增加label来描述节点本身的类型
   * neo4j支持给边增加任意数量kv形式的属性
   * neo4j中的边连接任意两个节点的有向边，可以重复、可以指向自身
   * cypther支持给label建立索引，并以类似于sql的形式进行复杂查询
1. 关系网络初始化与发展方案：
   * 使用一个数据库存储各种预设初始化
1. 每次执行发展程序时：
   * 生成新数据库（随机或从预设数据库读取）
      ```python
      # 对于每一时刻
      for t in range(time_length):
         # 回合开始阶段
         for n in nodes:
            # 复制当前节点
            y = class node(n)
            # 根据触发顺序计算回合开始阶段的状态变化
            for i in list_changes:
               # 查询获得所有关联信息
               x = cypher(i)
               # 根据节点状态和连接状态计算出当前时刻节点状态
               y = f(x, y)
            # 更新时间戳属性并插入数据库中
            insert_into_neo4j(y)
         # 回合进行阶段，与回合开始阶段内容相似，但是需要计算的状态不同
         for ... 
         # 回合结束阶段
         for ...
      ```
1. 可视化发展结果：
   * 指定数据库后，按照时间戳依次读取数据库中的节点，并可视化

