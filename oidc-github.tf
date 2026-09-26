# ------------------------------------------------------------------------------
# 1. AWS IAM OpenID Connect Provider for GitHub Actions
# ------------------------------------------------------------------------------
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]

  # Standard GitHub OIDC thumbprints
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a2a8515a67a0025fa2f4e0071d4516131156"
  ]

  tags = {
    Name      = "GitHubActions-OIDC-Provider"
    ManagedBy = "Terraform"
  }
}

# ------------------------------------------------------------------------------
# 2. IAM Role Trust Policy for GitHub Actions
# ------------------------------------------------------------------------------
data "aws_iam_policy_document" "github_oidc_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    # Restrict audience to AWS STS
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # Scoped to specified GitHub org/repo and branches/environments
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = var.github_subject_claims
    }
  }
}

# ------------------------------------------------------------------------------
# 3. IAM Role for Terraform Deployments
# ------------------------------------------------------------------------------
resource "aws_iam_role" "github_actions" {
  name               = var.role_name
  description        = "IAM Role assumed by GitHub Actions for automated Terraform deployments"
  assume_role_policy = data.aws_iam_policy_document.github_oidc_assume_role.json

  tags = {
    Name      = var.role_name
    ManagedBy = "Terraform"
  }
}

# ------------------------------------------------------------------------------
# 4. Attach IAM Policy (Custom or AdministratorAccess)
# ------------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "github_actions_policy" {
  role       = aws_iam_role.github_actions.name
  policy_arn = var.policy_arn
}
