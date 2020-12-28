import os
from pandas import DataFrame, to_datetime
parents = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(parents, 'ResultPlot', '2020')
dirs = os.listdir(output_path)

full_data = []
for dirname in dirs:
    for second_dirname in os.listdir(os.path.join(output_path, dirname)):
        if os.path.isdir(os.path.join(output_path, dirname, second_dirname)):
            for filename in os.listdir(os.path.join(output_path, dirname, second_dirname)):
                # print(os.path.join(output_path, dirname, second_dirname, filename))
                if '.txt' in filename:
                    with open(os.path.join(output_path, dirname, second_dirname, filename), 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        data = lines[-1].strip().split(',')
                        try:
                            full_data.append({'Date':to_datetime(data[0]).strftime('%Y-%m-%d'), 'Method':filename.split('.')[0], 'Tickers':data[1:]})
                        except:
                            full_data.append({'Date':to_datetime(data[0][1:]).strftime('%Y-%m-%d'), 'Method':filename.split('.')[0], 'Tickers':data[1:]})

DataFrame(full_data).to_csv(os.path.join(parents, 'Selection_Collections.csv'), index=False)
                