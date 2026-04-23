# Lab 16 — Detailed Analysis Report

> Breakdown of benchmark results by question difficulty, question type, and failure modes.

## 1. Performance by Difficulty Level

### ReAct Agent
| Difficulty | Count | EM | Avg Tokens | Avg Latency (ms) |
|---|---:|---:|---:|---:|
| Easy | 33 | 81.8% | 1,521.9 | 2,499.5 |
| Medium | 34 | 82.3% | 1,658.6 | 2,692.1 |
| Hard | 33 | 75.8% | 1,801.6 | 5,793.5 |

### Reflexion Agent
| Difficulty | Count | EM | Avg Attempts | Avg Tokens | Avg Latency (ms) |
|---|---:|---:|---:|---:|---:|
| Easy | 33 | 93.9% | 1.21 | 1,901.8 | 7,669.8 |
| Medium | 34 | 88.2% | 1.29 | 2,355.3 | 6,119.6 |
| Hard | 33 | 84.9% | 1.39 | 2,710.2 | 6,622.0 |

### Reflexion Improvement Over ReAct (Delta EM)
| Difficulty | ReAct EM | Reflexion EM | Delta | Improvement |
|---|---:|---:|---:|---|
| Easy | 81.8% | 93.9% | +12.1% | ██████ |
| Medium | 82.3% | 88.2% | +5.9% | ██ |
| Hard | 75.8% | 84.9% | +9.1% | ████ |

## 2. Performance by Question Type

### ReAct Agent
| Type | Count | EM | Avg Tokens | Avg Latency (ms) |
|---|---:|---:|---:|---:|
| Bridge | 51 | 78.4% | 1,774.8 | 4,929.8 |
| Comparison | 49 | 81.6% | 1,541.9 | 2,322.1 |

### Reflexion Agent
| Type | Count | EM | Avg Attempts | Avg Tokens | Avg Latency (ms) |
|---|---:|---:|---:|---:|---:|
| Bridge | 51 | 82.3% | 1.39 | 2,687.1 | 6,258.6 |
| Comparison | 49 | 95.9% | 1.20 | 1,943.5 | 7,357.2 |

### Delta by Question Type
| Type | ReAct EM | Reflexion EM | Delta |
|---|---:|---:|---:|
| Bridge | 78.4% | 82.3% | +3.9% |
| Comparison | 81.6% | 95.9% | +14.3% |

## 3. Failure Modes by Difficulty

### ReAct
| Difficulty | Entity Drift | Incomplete Multi Hop | Wrong Final Answer | Total Failures |
|---|---:|---:|---:|---:|
| Easy | 6 | 6 | 6 | 18 |
| Medium | 6 | 2 | 5 | 13 |
| Hard | 7 | 4 | 7 | 18 |

### Reflexion
| Difficulty | Entity Drift | Incomplete Multi Hop | Looping | Wrong Final Answer | Total Failures |
|---|---:|---:|---:|---:|---:|
| Easy | 4 | 5 | 2 | 5 | 16 |
| Medium | 2 | 1 | 4 | 4 | 11 |
| Hard | 1 | 2 | 5 | 9 | 17 |

## 4. Cross-Analysis: Difficulty × Question Type

### ReAct EM by Difficulty × Type
| Difficulty | Bridge | Comparison |
|---|---:|---:|
| Easy | 82% (n=17) | 81% (n=16) |
| Medium | 76% (n=17) | 88% (n=17) |
| Hard | 76% (n=17) | 75% (n=16) |

### Reflexion EM by Difficulty × Type
| Difficulty | Bridge | Comparison |
|---|---:|---:|
| Easy | 88% (n=17) | 100% (n=16) |
| Medium | 76% (n=17) | 100% (n=17) |
| Hard | 82% (n=17) | 88% (n=16) |

## 5. Notable Examples

### Cases Corrected by Reflexion

**Q: Were Winter Soldier and Fahrenheit 9/11 about the same country's wars?**
- Difficulty: `hard` | Type: `comparison`
- Gold: `yes`
- ReAct answer: `No` ❌
- Reflexion answer: `Yes, both about U.S. wars` ✅ (after 2 attempt(s))

**Q: What did Both Dumitru Prunariu and Claude Nicollier had in common?**
- Difficulty: `hard` | Type: `comparison`
- Gold: `flew in space`
- ReAct answer: `Both are astronauts` ❌
- Reflexion answer: `Both flew in space` ✅ (after 2 attempt(s))

**Q: In what country can both Oplismenus and Aerangis.be found to be growing?**
- Difficulty: `medium` | Type: `comparison`
- Gold: `Africa`
- ReAct answer: `Cameroon and Gabon` ❌
- Reflexion answer: `Africa` ✅ (after 2 attempt(s))

**Q: What type of media does Mr Hudson and Makethisrelate have in common?**
- Difficulty: `medium` | Type: `comparison`
- Gold: `music`
- ReAct answer: `Music videos` ❌
- Reflexion answer: `Music` ✅ (after 2 attempt(s))

**Q: Are Calceolaria and Arrhenatherum both flowers?**
- Difficulty: `easy` | Type: `comparison`
- Gold: `no`
- ReAct answer: `No, only Calceolaria` ❌
- Reflexion answer: `No, only Calceolaria is a flower` ✅ (after 2 attempt(s))

**Q: What are Hypoestes and Cycad ?**
- Difficulty: `easy` | Type: `comparison`
- Gold: `plants`
- ReAct answer: `Cycads: seed plants; Hypoestes: flowering plants` ❌
- Reflexion answer: `Plant genera` ✅ (after 2 attempt(s))

### Persistent Failures (Both Agents Wrong)

**Q: Who was with the cosmonaut who commanded the historic Voskhod 2 mission which saw the first man walk in space in 1965 ?**
- Difficulty: `easy` | Type: `bridge`
- Gold: `Alexey Leonov`
- ReAct answer: `Pavel Belyayev` ❌ (entity_drift)
- Reflexion answer: `Pavel Belyayev` ❌ (looping, 3 attempts)

**Q: Which film did Eileen Heckart star in three years before The Bad Seed?**
- Difficulty: `easy` | Type: `bridge`
- Gold: `"Picnic"`
- ReAct answer: `Up the Down Staircase` ❌ (entity_drift)
- Reflexion answer: `Up the Down Staircase` ❌ (looping, 3 attempts)

**Q: Who released the song before "Out of the Woods" on the album "1989" to radio? **
- Difficulty: `medium` | Type: `bridge`
- Gold: `Republic Records`
- ReAct answer: `Blank Space` ❌ (entity_drift)
- Reflexion answer: `Blank Space` ❌ (looping, 3 attempts)

## 6. Key Takeaways

1. **Difficulty Impact**: Reflexion shows the largest improvement on **easy** questions (Δ = +12.1%), suggesting that reflection is most valuable when initial reasoning is more likely to go wrong.

2. **Question Type**: **Comparison** questions benefit most from Reflexion (Δ = +14.3%). This is expected because comparison questions require precise identification of shared/distinct properties.

3. **Failure Patterns**: The most common failure mode across all difficulties is **entity_drift** (agent latches onto a plausible but wrong entity from context). Reflexion reduces entity_drift but can introduce **looping** when reflection fails to surface novel strategies.

4. **Cost-Benefit**: Reflexion uses ~40% more tokens than ReAct. The +9% EM improvement is significant for high-stakes QA but may not justify the cost for simple questions where ReAct already achieves high accuracy.
