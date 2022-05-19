resource "aws_ecr_repository" "nginx" {
  name                 = "djangotestnginx"
  image_tag_mutability = "MUTABLE"


  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "python" {
  name                 = "djangotestpython"
  image_tag_mutability = "MUTABLE"


  image_scanning_configuration {
    scan_on_push = true
  }
}
