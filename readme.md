representation of culture 
a list of five digits 

caculate culture simmialiry whether or not its the same 

site only interact with directly neighbours 
a typical site has four neighbours 
10 10 grid 

interactions 

At random, pick a site to be active, and pick one of its neighbors.
Step 2. With probability equal to their cultural similarity, these two sites interact. An
interaction consists of selecting at random a feature on which the active site and its
neighbor differ (if there is one) and changing the active site's trait on this feature to the
neighbor's trait on this feature.

example, if the first feature was the one to change, then the value of 6 from the
neighbor's first feature would become the value of the first feature of the underlined
site, changing its culture from 82330 to 62330. This change will increase the cultural
similarity of these two sites from 40% to 60%, making it even easier for them to
converge still further.5


At random, pick a site to be active, and pick one of its neighbors

在 (A) 里，边角 site 的每个邻居被选中的概率更高。比如角上的 site 只有 2 个邻居，每个邻居有 1/2 概率被选；内部 site 有 4 个邻居，每个邻居只有 1/4 概率。所以角落附近的交互比内部密集。
Axelrod 其实明确选了 (A)，原文第 209 页：

"Note that the activated site, rather than its neighbor, is the one that may undergo change. This is done to guarantee that each site has an equal chance of being a candidate for social influence, even though the sites on the edge of the map have fewer neighbors than sites in the interior."

所以这不是"模糊"，是 Axelrod 刻意设计。但值得讨论的是：谁改变也是一个选择。


3. Trait 的表示：是否有序？（★★ 很重要）
原文用数字 0-9 表示 traits，但这只是标签，不是数值。论文第 208 页：

"this feature has the eighth of its possible values"

Trait "8" 和 trait "2" 不比 "8" 和 "7" 更远——全都是"要么相同、要么不同"的二元关系。
潜在的替代实现：如果把 traits 当成有序的（比如把 culture 看成连续值，交互时是向邻居"靠近"而不是"复制"），会变成一个完全不同的模型（像 bounded confidence 模型）。Axelrod 的贡献之一就是强调离散、无序。
这个值得写进反思，说明你理解了 representation 的选择。

4. 边界条件：torus 还是有界？（★）
原文默认有界（边角邻居少）。但第 215 页讨论稳定区域数量时说：

"Boundaries can be eliminated by wrapping around... Simulations with this neighborhood topology show the same pattern as before."

所以 Axelrod 自己也测了 torus 版本，结论相似但峰值位置略不同。你可以在 app.py 里加一个 torus 的 toggle，成本很低，能产出一个对比图。

6. "Event" 的时间尺度（★★）
我们现在一步 = width × height 个 events（平均每个 site 激活一次）。但原文 Figure 1 是以"events"为时间单位（一次一个 event）。这在 Mesa 的 step 框架下有点不自然。
可以讨论的点：

Asynchronous update（Axelrod 原版）vs synchronous update（所有 agent 同时用旧状态决定新状态）
原文 footnote 5 特意说用 asynchronous 避免"synchronous activation 的 artifacts"，引用了 Huberman and Glance 1993

这是 Miller & Page 文章里也强调的 timing 问题（synchronous / async-random / async-incentive），可以把两篇论文联系起来。

7. "Stable" 的判定：定义清楚但实现有选择（☆）
is_stable 每步都查一遍整个 grid，O(N²) 成本。可以讨论：

是否应该只在"没有发生变化"时才检查
增量维护一个"不稳定邻居对"的集合


3. Similarity 的定义：匹配比例 vs. 原文 footnote 4 的实现
原文正文："the percentage of their features that have the identical trait"
原文 footnote 4（实际实现）：

"Select a random site (s), a random neighbor of that site (n), and a random feature (f). ... This implementation of the model takes advantage of that fact that the probability that a random feature f will have the same trait at two sites equals the cultural similarity between those two sites."

翻译：Axelrod 的实际代码是先随机挑一个 feature f，如果 c(s,f) = c(n,f)（两者在 f 上相同）且还有别的 feature 不同，就从其他不同的 feature 里挑一个复制。
他说这"利用了一个事实"——随机挑 feature 时相等的概率就等于 similarity。所以不用显式计算 similarity。
我写的实现：显式计算 similarity = 匹配数 / 总数，然后用这个概率决定是否交互。
两种在概率分布上完全等价，但我这个写法和原文 footnote 4 的实现路径不同。严格说这算我替你拍板了——我选了"直观版"而不是"footnote 4 版"。
值得写进反思：说明你读了 footnote 4，知道有两种等价写法，你选了可读性更好的那个。

4. 邻域形状：von Neumann 还是 Moore？
原文："A typical site has four neighbors (north, east, south, and west)"
这个倒是说死了——4 邻居。但原文后面讨论 range of interaction 时有提到 8 邻居和 12 邻居的扩展版。
我拍板：只用 4 邻居（符合基本模型）。
可选：你可以把 moore 做成参数，让用户在 GUI 里切换 4/8 邻居，复现原文"larger neighborhoods → fewer stable regions"的结论。 slider 