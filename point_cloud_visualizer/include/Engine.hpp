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

    comptr<ID3D11SamplerState> m_wrapSampler{};

    pcviz::GraphicsPipeline m_pipeline{};
    pcviz::ConstantBuffer<pcviz::SceneBuffer> m_sceneBuffer{};

    comptr<ID3D11ShaderResourceView> m_texture{};
    comptr<ID3D11ShaderResourceView> m_depthMap{};
    uint32_t m_verticesCount{};

    comptr<ID3D11BlendState> m_blendState{};
};
