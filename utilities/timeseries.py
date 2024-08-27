# class TimeSeries : 
#     topic = "timeSeries"
#     def collectData(self , sensor_id, payload):
#         try:
#             print(f"Collected data from flora {payload}")
#             if sensor_id not in data_storage:
#                 data_storage[sensor_id] = []
#                 data_storage[sensor_id].append({
#                 "temperature": payload["temperature"],
#                 "moisture": payload["moisture"],
#                 "timestamp": payload["timestamp"]
#             })
#             print(f"Structure of data collected: {data_storage}")
#             return True
#         except Exception as e:
#             print(f"ERR collect payload: {e}")