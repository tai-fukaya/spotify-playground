//
//  FirstViewController.swift
//  songinfo
//
//  Created by groovex on 2018/12/23.
//  Copyright © 2018年 groovex. All rights reserved.
//

import UIKit
import MediaPlayer

class AlbumItem {
    var persistentID: MPMediaEntityPersistentID = 0
    var title: String = ""
    var artist: String = ""
    var playCount: Int = 0
    var playTime: TimeInterval = 0
    var dateAdded: Date = Date()
    var releaseDate: Date = Date()
    
    init() {
        
    }
}


class FirstViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        self.view.backgroundColor = .yellow
        
        let status = MPMediaLibrary.authorizationStatus()

        switch status {

        case .authorized:
            self.completion()
            break

        // 初回起動時はnotDetermined
        case .notDetermined:
            MPMediaLibrary.requestAuthorization { status in
                if status == .authorized {
                    self.completion()
                }
            }
            break

        // 一度拒否されている場合
        case .denied, .restricted:
            break
        }
    }
    
    func completion() {
        let artistsQuery = MPMediaQuery.artists()
        let artists = artistsQuery.collections
        print(String(artists!.count) + " artists")

        let albumsQuery = MPMediaQuery.albums()
        let albums = albumsQuery.collections
        print(String(albums!.count) + " albums")

        let songsQuery = MPMediaQuery.songs()
        let songs = songsQuery.items
        print(String(songs!.count) + " songs")

        let formatter = DateFormatter()
        formatter.locale = NSLocale(localeIdentifier: "ja_JP") as Locale
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        let begin = formatter.date(from: "2020-01-01 00:00:00")
        let end = formatter.date(from: "2021-01-01 00:00:00")
        var refinedSongs = [MPMediaItem]()
        var refinedAlbums = [MPMediaEntityPersistentID:AlbumItem]()
        for song in songs! {
            if (song.dateAdded > begin! && song.dateAdded < end!) {
                refinedSongs.append(song)
                let albumPID = song.albumPersistentID
                if (refinedAlbums.index(forKey: albumPID) == nil) {
                    let album = AlbumItem()
                    album.persistentID = albumPID
                    album.title = song.albumTitle ?? ""
                    album.artist = song.albumArtist ?? ""
                    album.dateAdded = song.dateAdded
                    album.releaseDate = song.releaseDate ?? Date()

                    refinedAlbums[albumPID] = album
                }
                let album = refinedAlbums[albumPID]
                album?.playCount += song.playCount
                album?.playTime += Double(song.playCount) * song.playbackDuration
            }
        }
        refinedSongs.sort(by: {
            $0.playCount > $1.playCount
        })
        print(String(refinedSongs.count) + " tracks")
        for i in 0...10 {
            let op:[String] = [String(i+1), refinedSongs[i].title ?? "", refinedSongs[i].artist ?? "", String(refinedSongs[i].playCount), formatter.string(from: refinedSongs[i].dateAdded)]
            print(op.joined(separator: "\t"))
        }
        var sortedAlbums = refinedAlbums.sorted(by: {
            $0.1.playCount > $1.1.playCount
        })
        print(String(refinedAlbums.count) + " albums")
       for obj in sortedAlbums {
           let album = obj.value
           let op:[String] = [album.title, album.artist, String(album.playCount), formatter.string(from: album.releaseDate), formatter.string(from: album.dateAdded)]
           print(op.joined(separator: "\t"))
       }
    }

}

