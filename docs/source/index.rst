.. toctree::
   :maxdepth: 4
   :hidden:

   rider

rider
=====

This is docs/index.rst, documenting the Rider project.

Ноутбук
-------

Текущая версия используется в `Google Colab <https://colab.research.google.com/drive/1o_C-fdRLY1EMGcQlLEhg065IhT4hsBPp#scrollTo=H9lgHtCHp8Dv>`_.

Пример использования:


.. code-block:: python

   from rider import get_dataset, make_subset, default_results
   df_full, vehicle_type = get_dataset(RAW_DATA_URL, DATA_FOLDER)
   subset_df = make_subset(df_full, vehicle_type, DAYS, TYPES)
   (trip_df, pairs_df), (trips, routes, milages) = default_results(subset_df)
 

Идеи и ключевые слова
---------------------

Расстояния между кривыми:

- Hausdorff distance
- Fréchet distance


Описание алгоритма
------------------

- Прочли сырые данные из JSON, создали два табличных файла
- Преобразовали исходные данные в список треков `List[Route: pd.DataFrame]`
- Составляем все пары треков, количество таких пар будет равно `n * (n-1) / 2`
- Проводим анализ фигур треков в два этапа:
  - выбраковываем непересекающиеся треки (в грубой апроксимации треков)
  - оцениваем близость фигур оставшихся пар треков (в более точной апрокимации треков)
- Внутри каждой пары треков получаем коэффициенты сходимости треков
- Добавляем данные о длине треков, рассчитываем дополнительный коэффициент перекрытия с учетом длины
- Сделали две выгрузки датавреймов про сами терки и про найденные парные харакетристики

Гипотезы и упрощения:

- Смотрим путь машины внутри суток без учета разных заказов (объединяем заказы в один в течение суток)
