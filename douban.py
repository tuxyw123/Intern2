import requests
from bs4 import BeautifulSoup
import time
import random
from collections import Counter
import matplotlib.pyplot as plt
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def crawl_douban_movies():   
    movies = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for page in range(1, 3):  # 每页25部，爬取2页=50部
        url = f'https://movie.douban.com/top250?start={(page-1)*25}'
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = soup.find_all('div', class_='item')
            
            for item in items:
                try:
                    title = item.find('span', class_='title').text.strip()
                    info = item.find('div', class_='bd').p.text.strip()
                    lines = info.split('\n')
                    director_actor = lines[0].strip()
                    year_country = lines[1].strip() if len(lines) > 1 else ""

                    director = "未知"
                    if '导演: ' in director_actor:
                        director_part = director_actor.split('导演: ')[1]
                        if '主演:' in director_part:
                            director = director_part.split('主演:')[0].strip()
                        else:
                            director = director_part.strip()

                    actors = []
                    if '主演: ' in director_actor:
                        actors_part = director_actor.split('主演: ')[1]
                        actors_text = actors_part.split('...')[0] if '...' in actors_part else actors_part
                        actors_list = [actor.strip() for actor in actors_text.split('/')]

                        for actor in actors_list[:3]:  # 取前3个演员
                            if ' ' in actor and any(c.isascii() for c in actor):
                                chinese_part = actor.split(' ')[0]  
                                if chinese_part and not chinese_part.isascii():
                                    actors.append(chinese_part)
                            else:
                                if actor and not actor.isascii():
                                    actors.append(actor)

                    country = "未知"
                    if year_country:
                        parts = year_country.split('/')
                        if len(parts) > 1:
                            country_part = parts[1].strip()
                            if ' ' in country_part:
                                country = country_part.split(' ')[0]
                            else:
                                country = country_part

                    genre = ["剧情"]  # 默认类型
                    if len(lines) > 2:
                        genre_line = lines[2].strip()
                        if genre_line:
                            genres = [g.strip() for g in genre_line.split('/')]
                            genre = [g for g in genres if g and not g.isdigit()]
                    
                    movie = {
                        'title': title,
                        'director': director,
                        'actors': actors,
                        'country': country,
                        'genre': genre
                    }
                    
                    movies.append(movie)
                    
                except Exception as e:
                    continue

            time.sleep(random.uniform(1, 3))  # 随机延迟
            
        except Exception as e:
            print(f"爬取第{page}页失败: {e}")
            continue
    
    # 保存数据
    with open('douban_movies.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    
    print(f"爬取完成，共获取{len(movies)}部电影数据")
    return movies

def analyze_and_show(movies):

    # 统计
    all_actors = []
    directors = []
    countries = []
    all_genres = []
    
    for movie in movies:
        all_actors.extend(movie['actors'])
        directors.append(movie['director'])
        countries.append(movie['country'])
        all_genres.extend(movie['genre'])
    
    actor_counts = Counter(all_actors)
    director_counts = Counter(directors)
    country_counts = Counter(countries)
    genre_counts = Counter(all_genres)

    print("\n" + "="*50)
    print("豆瓣Top200电影分析结果")
    print("="*50)
    
    print("\n【出演次数最多的演员】")
    for i, (actor, count) in enumerate(actor_counts.most_common(5), 1):
        print(f"{i}. {actor} - {count}部电影")
    
    print("\n【制片最多的国家】")
    for i, (country, count) in enumerate(country_counts.most_common(5), 1):
        print(f"{i}. {country} - {count}部电影")
    
    print("\n【出现次数最多的导演】")
    for i, (director, count) in enumerate(director_counts.most_common(5), 1):
        print(f"{i}. {director} - {count}部电影")
    
    print("\n【各类型电影数量】")
    for i, (genre, count) in enumerate(genre_counts.most_common(8), 1):
        print(f"{i}. {genre} - {count}部电影")

    print("\n生成图表...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 演员图表
    top_actors = dict(actor_counts.most_common(5))
    if top_actors:
        valid_actors = {k: v for k, v in top_actors.items() if k and k.strip() and len(k.strip()) > 1}
        if valid_actors:
            ax1.bar(valid_actors.keys(), valid_actors.values())
            ax1.set_title('出演次数最多的演员')
            ax1.tick_params(axis='x', rotation=45)
        else:
            ax1.text(0.5, 0.5, '演员数据不足', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('出演次数最多的演员')
    else:
        ax1.text(0.5, 0.5, '无演员数据', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('出演次数最多的演员')
    
    # 国家图表
    top_countries = dict(country_counts.most_common(5))
    if top_countries:
        valid_countries = {k: v for k, v in top_countries.items() if k and k.strip()}
        if valid_countries:
            ax2.bar(valid_countries.keys(), valid_countries.values())
            ax2.set_title('制片最多的国家')
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.text(0.5, 0.5, '国家数据不足', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('制片最多的国家')
    else:
        ax2.text(0.5, 0.5, '无国家数据', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('制片最多的国家')
    

    top_directors = dict(director_counts.most_common(5))
    if top_directors:
        valid_directors = {k: v for k, v in top_directors.items() if k and k.strip()}
        if valid_directors:
            ax3.bar(valid_directors.keys(), valid_directors.values())
            ax3.set_title('出现次数最多的导演')
            ax3.tick_params(axis='x', rotation=45)
        else:
            ax3.text(0.5, 0.5, '导演数据不足', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('出现次数最多的导演')
    else:
        ax3.text(0.5, 0.5, '无导演数据', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('出现次数最多的导演')
    
    # 类型图表
    top_genres = dict(genre_counts.most_common(8))
    if top_genres:
        valid_genres = {k: v for k, v in top_genres.items() if k and k.strip()}
        if valid_genres:
            ax4.bar(valid_genres.keys(), valid_genres.values())
            ax4.set_title('各类型电影数量')
            ax4.tick_params(axis='x', rotation=45)
        else:
            ax4.text(0.5, 0.5, '类型数据不足', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('各类型电影数量')
    else:
        ax4.text(0.5, 0.5, '无类型数据', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('各类型电影数量')
    
    plt.tight_layout()
    plt.savefig('douban_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ 图表已保存为 douban_analysis.png")

def main():
   
    # 爬取数据
    movies = crawl_douban_movies()
    
    if movies:
        # 分析并显示结果
        analyze_and_show(movies)
        print("\n分析完成")
    else:
        print("爬取失败，请检查网络连接")

if __name__ == "__main__":
    main()
