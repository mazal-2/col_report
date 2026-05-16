# -*- coding: utf-8 -*-
# User-provided correct revenue values (advertising revenue in yuan)
# Row: (账号, 剧目, 播放量, 广告收益_元)
data = [
    ('南瓜动漫短剧场（原创）', '祭品公主的生存法则', 11026, 6.04),
    ('爱动漫微剧场（二创）', '祭品公主的生存法则', 2583, 0.05),
    ('南瓜动漫短剧场（原创）', '替嫁后，沉睡老公超会撩', 120532, 79.51),
    ('爱动漫微剧场（二创）', '替嫁后，沉睡老公超会撩', 107152, 45.89),
]

print('=== 各行万播收益计算 ===')
for account, drama, play, rev in data:
    wanbo = rev / play * 10000
    print(f'{account} | {drama}: {rev} / {play} * 10000 = {wanbo:.4f}')

print()
print('=== 合计计算 ===')
orig_rev = 6.04 + 79.51
erc_rev = 0.05 + 45.89
orig_play = 11026 + 120532
erc_play = 2583 + 107152

print(f'原创合计: 收益={orig_rev}元, 播放={orig_play}')
print(f'二创合计: 收益={erc_rev}元, 播放={erc_play}')

orig_wanbo = orig_rev / orig_play * 10000
erc_wanbo = erc_rev / erc_play * 10000
orig_erc_total_wanbo = (orig_rev + erc_rev) / (orig_play + erc_play) * 10000

print(f'原创合计万播: {orig_rev} / {orig_play} * 10000 = {orig_wanbo:.4f}')
print(f'二创合计万播: {erc_rev} / {erc_play} * 10000 = {erc_wanbo:.4f}')
print(f'全部合计万播: {orig_rev+erc_rev} / {orig_play+erc_play} * 10000 = {orig_erc_total_wanbo:.4f}')

print()
print('=== 最终汇总表 ===')
print(f'{"账号":<20} {"剧目":<20} {"播放量":>8} {"广告收益(元)":>12} {"万播收益":>12}')
print('-' * 80)
for account, drama, play, rev in data:
    wanbo = rev / play * 10000
    print(f'{account:<20} {drama:<20} {play:>8,} {rev:>12.2f} {wanbo:>12.4f}')
print('-' * 80)
print(f'{"南瓜动漫短剧场（合计）":<20} {"两剧合计":<20} {orig_play:>8,} {orig_rev:>12.2f} {orig_wanbo:>12.4f}')
print(f'{"爱动漫微剧场（合计）":<20} {"两剧合计":<20} {erc_play:>8,} {erc_rev:>12.2f} {erc_wanbo:>12.4f}')
print(f'{"全部合计":<20} {"两剧合计":<20} {orig_play+erc_play:>8,} {orig_rev+erc_rev:>12.2f} {orig_erc_total_wanbo:>12.4f}')