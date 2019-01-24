import geopandas as gpd
import numpy as np


def processing(df_extra, df_sw):
    extra_pt = []
    for item in df_extra['geometry']:
        extra_pt.append(item)

    gdf = gpd.GeoDataFrame(df_sw, geometry='geometry')
    extra_array = np.empty((df_sw.shape[0],), object)

    project_pt = []
    sidewalk_id = []

    for idx, row in df_extra.iterrows():
        """
        Parse through all the points in df_fountain, enlarge
        the point by with a box area, find the sidewalks which
        intersects with the box. Calculate the distance from the 
        point to each of them and sorted from smallest to largest.

        """
        r = 10 ** (-3)  # buffer size
        p = row['geometry']
        bbox = [p.x - r, p.y - r, p.x + r, p.y + r]

        query = gdf.sindex.intersection(bbox, objects=True)
        sw_bbox = gdf.loc[[q.object for q in query]].geometry

        while len(sw_bbox.distance(p).sort_values()) == 0:
            r += 10 ** (-3)
            bbox = [p.x - r, p.y - r, p.x + r, p.y + r]
            query = gdf.sindex.intersection(bbox, objects=True)
            sw_bbox = df_sw.loc[[q.object for q in query]].geometry

        closest_dist_idx = sw_bbox.distance(p).sort_values().index[0]
        # print(closest_dist_idx)
        closest_row = gdf.loc[closest_dist_idx]
        # print(closest_row)

        new_point = closest_row['geometry'].interpolate(closest_row['geometry'].project(p))
        sidewalk_id.append(closest_dist_idx)
        project_pt.append(new_point)

        if extra_array[closest_dist_idx] is None:
            extra_array[closest_dist_idx] = []
        extra_array[closest_dist_idx].append(idx)

    return sidewalk_id, project_pt, extra_array




def main():

    fountain_file = "external data/Drinking Fountain.geojson"
    restroom_file = "external data/Public Restroom.geojson"
    sidewalks_file = "raw data/sidewalk_amend.geojson"

    df_fountain = gpd.read_file(fountain_file)
    df_restroom = gpd.read_file(restroom_file)
    df_sw = gpd.read_file(sidewalks_file)

    fountain_sidewalk_id, fountain_project_pt, fountain_array = processing(df_fountain, df_sw)

    restroom_sidewalk_id, restroom_project_pt, restroom_array = processing(df_restroom, df_sw)

    df_fountain['closest sidewalk id'] = fountain_sidewalk_id
    df_fountain['closest sidewalk point'] = fountain_project_pt

    df_restroom['closest sidewalk id'] = restroom_sidewalk_id
    df_restroom['closest sidewalk point'] = restroom_project_pt

    df_sw['drinking_fountain'] = fountain_array
    df_sw['public_restroom'] = restroom_array
    df_sw.to_csv("output/new_sw_wth_fountain_restroom.csv", encoding='utf-8')


if __name__ == '__main__':
    main()
