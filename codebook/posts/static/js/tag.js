function TagViewModel(data) {
    var self = this;
    self.tag = data['tag'];
    self.isTrending = data['is_trending'];
    self.tagUrl = data['url'];

    return self;
}