import requests
import json 
import re 
import os
import sys
def delete_existing_json_file(folder_path):
    try:
        # List all files in the folder
        files = os.listdir(folder_path)

        if files:
            print(f"Deleting {len(files)} file(s) in {folder_path}")

            # Delete each file in the folder
            for file in files:
                file_path = os.path.join(folder_path, file)
                os.remove(file_path)

            print("Files deleted successfully.")
        else:
            print("No files found in the folder.")
    except Exception as e:
        print(f"An error occurred: {e}")

def re_generate_token(response):
    if response == 401:
        status_data = generate_token()
        if status_data == '200':
            print("the token has regenerated")
            generativedata()
        else:
            print(status_data)


def make_api_request(access_token,folder_path):

    url = "https://api.spotify.com/v1/search?q=telugusongs+2023+india&type=album&market=IN&limit=50&offset=10"
    

    headers = {
    "Authorization": f"Bearer {access_token}",    
    "Content-Type": "application/x-www-form-urlencoded"
    }
    print("received request to get search data")
    response = requests.get(url,headers=headers)
    album_list_info = []
    if response.status_code == 200:
        data = response.json()
        for record in data['albums']['items']:
            artist = []
            for artists in record['artists']:
                arts_info = {
                'artist_id': artists['id']
                }
                artist.append(arts_info)
            album_info = {
            "name": record["name"],
            "uri": record["uri"],
            'artistinfo' : artist
                    }
            album_list_info.append(album_info)
        print("completed request to get search top album data data")
        output_file_path = folder_path+"/search_data.json"
        try:
            with open(output_file_path, "w") as output_file:
                json.dump(data, output_file, indent=2)
        except Exception as e:
            print(f"An error occurred while writing to {output_file_path}: {e}")
        print("completed loading data into json")
        return album_list_info
        
        
    else:
        print("API Request Failed. Status Code:", response.status_code)
        print("Trigerring the regenerate token call")
        re_generate_token(response.status_code)

def fetching_albums(data,access_tokens,folder_path):
    uris = []
    complete_data = []
    album_data =[]
    for records in data:
        pulling_uri = records['uri']
        uri = re.search(r":([^:]+)$", pulling_uri)
        uri_full = uri.group(1)
        uris.append(uri_full)
    print("starting to get albums details")
    for uring in uris:
        urls = "https://api.spotify.com/v1/albums/"+uring+"?market=IN"
        headers = {
            "Authorization": f"Bearer  {access_tokens}",    
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        responses = requests.get(urls,headers=headers)
        if responses.status_code == 200:
            album_datas = responses.json()
            album_data.append(album_datas)
            print("sucessfully finished the job of getting only albums")
        else:
            print(responses.status_code)
            print("token expired closing the code.")
            sys.exit()
    output_file_path = folder_path+"/album_all_data_final.json"
    try:
        with open(output_file_path, "w") as output_file:
            json.dump(album_data, output_file, indent=2) 
    except Exception as e:
        print(f"An error occurred while writing to {output_file_path}: {e}")
        print("completed loading album data into json")

    print("starting to get albums details tracks")
    for uri in uris:
        urls = "https://api.spotify.com/v1/albums/"+uri+"/tracks?market=IN"
        headers = {
            "Authorization": f"Bearer  {access_tokens}",    
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = requests.get(urls,headers=headers)

        if response.status_code == 200:
            album_data = response.json()
            complete_data.append(album_data)
            print("sucessfully finished the job of getting albums")
        else:
            print(response.status_code)
            print("token expired closing the code.")
            sys.exit()
    output_file_path = folder_path+"/album_tracks_all_data_final.json"
    try:
        with open(output_file_path, "w") as output_file:
            json.dump(complete_data, output_file, indent=2)
            return complete_data
    except Exception as e:
        print(f"An error occurred while writing to {output_file_path}: {e}")
        print("completed loading data into json")
            

def transforming_data(json_data,folder_path):
    song_detail = []
    for record in json_data:
        for track in record.get('items',[]):
            artist_data = []
            for artist in track.get('artists',[]):
                a_data = {
                    "id": artist.get("id"),
                    "name": artist.get("name"),
                    "uri": artist.get("uri"),

                 }
                artist_data.append(a_data)

            song_data = {
                'id' : track.get('id'),
                'name': track.get('name'),
                "duration_ms" : track.get('duration_ms'),
                "artists": artist_data,
                "uri": track.get("uri"),
                }
            song_detail.append(song_data)

    print("completed transformation job, starting to load the data in json")
    output_file_path = folder_path+"/songdetails_final.json"
    try:
        with open(output_file_path, "w") as output_file:
            json.dump(song_detail, output_file, indent=2)
    except Exception as e:
        print(f"An error occurred while writing to {output_file_path}: {e}")
    return song_detail

def allsongs(json_data,access_token,folder_path):   
    artistis_information = []    
    for artist in json_data:
        for artisti_info in artist.get('artists'):
            art = {
                "id":artisti_info.get('id'),
                "name":artisti_info.get('name')
                }
            artistis_information.append(art)
    headers = {
            "Authorization": f"Bearer  {access_token}",    
            "Content-Type": "application/x-www-form-urlencoded"
        }
    output = folder_path + '/artists_info.json'
    print('job completed to pull artist info')
    try:
        with open(output, "w") as outpust:
            json.dump(artistis_information,outpust, indent=2)
    except Exception as e:
        print(f"An error occurred while writing to {output}: {e}")

    arts_data = []
    for art in artistis_information:
        ids = art.get('id')
        url = 'https://api.spotify.com/v1/artists/'+ids+'/top-tracks?market=IN'
    
        response = requests.get(url,headers=headers)

        if response.status_code == 200:
            artists_output = response.json()
            print('job is running to get album tracks')
            arts_data.append(artists_output)
        else:
            print("the error in the api call",response.status_code)
            print("token expired closing the code.")
            sys.exit()
    print('job completed')
    output = folder_path+'/all_songs_json.json'
    try:
        with open(output, "w") as output_file:
            json.dump(artists_output, output_file, indent=2)
    except Exception as e:
        print(f"An error occurred while writing to {output_file}: {e}")

def generate_token():
    if os.path.exists('C:/Users/Mohammed Ilham/Documents/DataAnalysis project/Project spotify/access_token.json'):
        os.remove('C:/Users/Mohammed Ilham/Documents/DataAnalysis project/Project spotify/access_token.json')
        print('accesstoken file is deleted')
    else:
        print("file not exisits")
    url = "https://accounts.spotify.com/api/token"

    client_id = "f4f8554077e84dc8a5fd740ea419bff8"
    client_secret = "afe443f1d33e46d6bbad9a7a319b4397"
    grant_type = "client_credentials"

    data = {
        "grant_type": grant_type,
        "client_id": client_id,
        "client_secret": client_secret
           }   

    headers = {
    "Content-Type": "application/x-www-form-urlencoded"
            }
    print('Recived client request to generate token')
    print("starting request to generate client token")
    response = requests.post(url, data=data, headers=headers)
    print("completed client request")
    if response.status_code == 200:
        print("status sucess",response.status_code)
        access_token = response.json().get("access_token")
        print("access token is generated")
        filepath = 'C:/Users/Mohammed Ilham/Documents/DataAnalysis project/Project spotify/access_token.json'
        with open(filepath, "w") as json_file:
            json.dump(access_token,json_file, indent=2)
            print("completed handling token generation saved the request")
            status = '200'
            
    else:
        print("Error:", response.status_code, response.text)
        status = 'ERROR'
    return status

def generativedata():
    # this is to check if the output file is present or not, if present the function will remove it
    print("starting to check if the any files are present")
    folder_path = 'C:/Users/Mohammed Ilham/Documents/DataAnalysis project/Project spotify/output_jsons'
    delete_existing_json_file(folder_path)
    print("sucessfully finished the job")
    # this step start to generate the access token
    print('sending client request to generate tokens')
    with open('C:/Users/Mohammed Ilham/Documents/DataAnalysis project/Project spotify/access_token.json', 'r') as token:
        access_tokens = json.load(token)
    # this steps start the first job to get the search results
    print("starting handling search request")
    data = make_api_request(access_tokens,folder_path)

    # finding the respective albums with the search results.
    print("starting to fetch the albums with uri")

    # finding the respective songs and artists of the albums
    album_output = fetching_albums(data,access_tokens,folder_path)

    #  to transform the output to the required data
    print("started handling transformation job")
    Result_with_artistic_data = transforming_data(album_output,folder_path)
    print("completed loading data")

    print("pulling the artist top tracks")
    allsongs(Result_with_artistic_data,access_tokens,folder_path)
    print("completed pulling the data of the artists top tracks")

def main():
    generativedata()
if __name__ == "__main__":
    main()