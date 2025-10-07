để bạn hiểu và tự tính được từng pha trong đoạn chạy (tăng tốc, đều, phanh), mình tóm công thức “chuẩn vật lý” cho profile 3 pha (trapezoid) mà mình đã dùng trong code:

---

## 1️⃣ Pha tăng tốc đều (0 → V)

Giả thiết:

- Gia tốc a = hằng
- Bắt đầu đứng yên
- Kết thúc tại vận tốc V trong thời gian (t_1)

[

V = a,t_1

]

Quãng đường pha tăng tốc:

[

s_1 = \tfrac12,a,t_1^2 = \tfrac12,V,t_1

]

---

## 2️⃣ Pha chạy đều (vận tốc = V)

Giả thiết: chạy đều V trong thời gian (t_2)

[

s_2 = V,t_2

]

---

## 3️⃣ Pha phanh đều (V → 0)

Giả thiết:

- Gia tốc phanh có độ lớn (a_b > 0)
- Thời gian phanh (t_b = V / a_b)

Quãng đường phanh:

[

s_b = \tfrac{V^2}{2,a_b}

]

---

## 4️⃣ Tổng quãng đường đoạn thẳng

Tổng:

[

S = s_1 + s_2 + s_b = \tfrac12 a t_1^2 + V t_2 + \tfrac{V^2}{2 a_b}

]

Thay (a = V/t_1):

[

S = \tfrac12 V t_1 + V t_2 + \tfrac{V^2}{2 a_b}

]

→ từ đây có thể giải ra (t_2) nếu biết S, V, t₁, a_b:

[

\boxed{t_2 = \frac{S - \tfrac12 V t_1 - \tfrac{V^2}{2 a_b}}{V}}

]

---

## 5️⃣ Trường hợp đoạn ngắn, không đạt V (tam giác)

Nếu (S < s_1 + s_b) → xe không đủ chỗ đạt đến V trước khi phải phanh.

Lúc đó ta tìm (V_{\max}) sao cho:

[

S = \frac{V_{\max}^2}{2 a} + \frac{V_{\max}^2}{2 a_b}

= \frac{V_{\max}^2}{2}\left(\frac{1}{a} + \frac{1}{a_b}\right)

]

[

\boxed{V_{\max} = \sqrt{\frac{2S}{\frac{1}{a}+\frac{1}{a_b}}}}

]

Khi đó:

[

t_{1,\text{eff}} = \frac{V_{\max}}{a},\qquad t_{b,\text{eff}} = \frac{V_{\max}}{a_b},\qquad t_2 = 0

]

---

## 6️⃣ Ý nghĩa trong chương trình C

- Dùng (t_1) **đo thực tế** (xe tăng tốc thật).
- Tính (a = V/t_1).
- Mỗi đoạn đường (S) (do Dijkstra tính ra = số ô × khoảng cách tâm-tâm (L)):
    - Nếu (S ≥ s_1 + s_b) → có cruise:
        - (t_2 = (S - s_1 - s_b)/V)
    - Nếu (S < s_1 + s_b) → không đạt V:
        - (V_{\max} = \sqrt{2S / (1/a + 1/a_b)})
        - (t_1 = V_{\max}/a,; t_b = V_{\max}/a_b,; t_2=0)

Sau đó mỗi đoạn được lập trình:

```
ACCEL t1
CRUISE t2
BRAKE tb

```

rồi quay hướng mới (`TURN LEFT/RIGHT`).

---

## 7️⃣ Khi đo thực tế

- t₁ đo bằng thời gian xe tăng từ 0 đến tốc độ hành trình mong muốn V.
- a_b (gia tốc phanh) đo bằng thời gian xe giảm từ V xuống 0 (tb = V/a_b).
- Khoảng cách mỗi ô (EDGE_M) = khoảng cách tâm-tâm giữa 2 điểm grid thật.
- Tổng S = số ô thẳng × EDGE_M (đoạn đó Dijkstra cho).

---

Tóm lại, ba công thức cốt lõi bạn cần nhớ:

[

\boxed{

\begin{aligned}

a &= \frac{V}{t_1} \

s_1 &= \tfrac12,V,t_1 \

s_b &= \frac{V^2}{2a_b} \

t_2 &= \frac{S - s_1 - s_b}{V}

\end{aligned}

}

]

và nếu không đủ dài:

[

\boxed{

V_{\max} = \sqrt{\frac{2S}{1/a + 1/a_b}}

}

]

![image.png](attachment:90a06b63-9912-45c9-b77a-32958bb43b02:image.png)
