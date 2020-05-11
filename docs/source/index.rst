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

Использование
-------------

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
