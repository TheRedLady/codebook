function AuthorViewModel(data) {
    var self = this;
    self.profileId = data['id'];
    self.fullName = data['full_name'];
    self.profileUrl = data['url'];

    return self;
}