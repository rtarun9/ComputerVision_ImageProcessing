#pragma once

#include "Application.hpp"

class Engine final : public pcviz::Application
{
  public:
    Engine(const std::string_view windowTitle);

    void loadContent() override;
    void update(const float deltaTime) override;
    void render() override;

  private:
    pcviz::DepthTexture m_depthTexture{};
    pcviz::RenderTarget m_renderTarget{};

    comptr<ID3D11Buffer> m_vertexBuffer{};
    comptr<ID3D11Buffer> m_indexBuffer{};

    comptr<ID3D11SamplerState> m_wrapSampler{};

    pcviz::GraphicsPipeline m_pipeline{};
    pcviz::ConstantBuffer<pcviz::SceneBuffer> m_sceneBuffer{};
    std::vector<float> m_depthData{};

    comptr<ID3D11ShaderResourceView> m_texture{};
    comptr<ID3D11ShaderResourceView> m_depthMap{};
    comptr<ID3D11ShaderResourceView> m_disparityMap{};

    uint32_t m_verticesCount{};
    uint32_t m_depthMapTexelCount{};
};
