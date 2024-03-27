filtered_tracks = []
    for track in recommendations['tracks']:
        duration_ms = track['duration_ms']
        popularity_number = track['popularity']
        if 'short' in duration and duration_ms <= 120000: # less than 2 minutes
            if 'popular' in popularity and popularity_number > 70:
                filtered_tracks.append(track)
            elif 'unpopular' in popularity and popularity_number < 30:
                filtered_tracks.append(track)
            elif 'no preference' in popularity:
                filtered_tracks.append(track)
        elif 'long' in duration and duration_ms > 240000: # more than 4 minutes
            if 'popular' in popularity and popularity_number > 70:
                filtered_tracks.append(track)
            elif 'unpopular' in popularity and popularity_number < 30:
                filtered_tracks.append(track)
            elif 'no preference' in popularity:
                filtered_tracks.append(track)
        elif 'no preference' in duration:
            if 'popular' in popularity and popularity_number > 70:
                filtered_tracks.append(track)
            elif 'unpopular' in popularity and popularity_number < 30:
                filtered_tracks.append(track)
            elif 'no preference' in popularity:
                filtered_tracks.append(track)

            
        
    if filtered_tracks:
        return render_template('results.html', playlist_data=filtered_tracks)
    else:
        return "No tracks found with the selected criteria. Please try again."