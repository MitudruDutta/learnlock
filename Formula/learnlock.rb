class Learnlock < Formula
  include Language::Python::Virtualenv

  desc "The app that argues with you. Adversarial Socratic learning CLI"
  homepage "https://github.com/MitudruDutta/learnlock"
  url "https://files.pythonhosted.org/packages/source/l/learnlock/learnlock-0.1.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "learnlock", shell_output("#{bin}/learnlock --help")
  end
end
