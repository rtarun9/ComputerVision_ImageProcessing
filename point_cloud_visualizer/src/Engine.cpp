#include "Pch.hpp"

#include "Engine.hpp"

#define STB_IMAGE_IMPLEMENTATION
#include <stb_image.h>

using namespace math;

Engine::Engine(const std::string_view windowTitle) : pcviz::Application(windowTitle) {}

void Engine::loadContent()
{
    m_wrapSampler = createSampler(pcviz::SamplerCreationDesc{
        .filter = D3D11_FILTER_MIN_MAG_MIP_POINT,
        .addressMode = D3D11_TEXTURE_ADDRESS_WRAP,
    });

    m_pipeline = createGraphicsPipeline(pcviz::GraphicsPipelineCreationDesc{
        .vertexShaderPath = L"shaders/TestShader.hlsl",
        .pixelShaderPath = L"shaders/TestShader.hlsl",
        .inputLayoutElements =
            {
                pcviz::InputLayoutElementDesc{.semanticName = "Position", .format = DXGI_FORMAT_R32G32_FLOAT, .inputClassification = D3D11_INPUT_PER_VERTEX_DATA},
                pcviz::InputLayoutElementDesc{.semanticName = "TextureCoord", .format = DXGI_FORMAT_R32G32_FLOAT, .inputClassification = D3D11_INPUT_PER_VERTEX_DATA},
            },
        .primitiveTopology = D3D11_PRIMITIVE_TOPOLOGY::D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST,
        .vertexSize = sizeof(pcviz::VertexPosTexCoord),
    });

    m_sceneBuffer = createConstantBuffer<pcviz::SceneBuffer>();

    m_depthTexture = createDepthTexture();

    m_renderTarget = createRenderTarget(m_windowWidth, m_windowHeight, DXGI_FORMAT_R8G8B8A8_UNORM_SRGB);

    m_texture = createTexture(L"../data/stereo/left_camera_view.jpg");
    int width{};
    int height{};
    int components{};

    const auto* data = stbi_loadf("../data/stereo/depth_map.hdr", &width, &height, nullptr, 1u);
    D3D11_TEXTURE2D_DESC textureDesc{};
    textureDesc.Width = width;
    textureDesc.Height = height;
    textureDesc.MipLevels = 1;
    textureDesc.ArraySize = 1;
    textureDesc.BindFlags = D3D11_BIND_SHADER_RESOURCE;

    textureDesc.Format = DXGI_FORMAT_R32_FLOAT;

    textureDesc.SampleDesc.Count = 1;
    textureDesc.Usage = D3D11_USAGE_DEFAULT;

    D3D11_SUBRESOURCE_DATA textureSubresourceData{};
    // subresource 0 is ready to be done is thread's work is already done
    textureSubresourceData.pSysMem = std::move(data);
    textureSubresourceData.SysMemPitch = width * sizeof(float);
    textureSubresourceData.SysMemSlicePitch = 0;

    // Create texture view
    D3D11_SHADER_RESOURCE_VIEW_DESC shaderResourceViewDesc = {};
    shaderResourceViewDesc.Format = textureDesc.Format;
    shaderResourceViewDesc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
    shaderResourceViewDesc.Texture2D.MipLevels = textureDesc.MipLevels;
    shaderResourceViewDesc.Texture2D.MostDetailedMip = 0;

    comptr<ID3D11Texture2D> texture{};
    throwIfFailed(m_device->CreateTexture2D(&textureDesc, &textureSubresourceData, &texture));

    throwIfFailed(m_device->CreateShaderResourceView(texture.Get(), &shaderResourceViewDesc, &m_depthMap));

    std::vector<pcviz::VertexPosTexCoord> vertexData{};

    vertexData.emplace_back(pcviz::VertexPosTexCoord{
        .position =
            {
                -1.0f,
                1.0f,
            },
        .texCoord = {0.0f, 0.0f},
    });
    vertexData.emplace_back(pcviz::VertexPosTexCoord{
        .position =
            {
                1.0f,
                1.0f,
            },
        .texCoord = {1.0f, 0.0f},
    });
    vertexData.emplace_back(pcviz::VertexPosTexCoord{
        .position =
            {
                -1.0f,
                -1.0f,
            },
        .texCoord = {0.0f, 1.0f},
    });
    vertexData.emplace_back(pcviz::VertexPosTexCoord{
        .position =
            {
                -1.0f,
                -1.0f,
            },
        .texCoord = {0.0f, 1.0f},
    });
    vertexData.emplace_back(pcviz::VertexPosTexCoord{
        .position =
            {
                1.0f,
                1.0f,
            },
        .texCoord = {1.0f, 0.0f},
    });
    vertexData.emplace_back(pcviz::VertexPosTexCoord{
        .position =
            {
                1.0f,
                -1.0f,
            },
        .texCoord = {1.0f, 1.0f},
    });

    m_vertexBuffer = createBuffer<pcviz::VertexPosTexCoord>(pcviz::BufferCreationDesc{.usage = D3D11_USAGE_IMMUTABLE, .bindFlags = D3D11_BIND_VERTEX_BUFFER}, vertexData);
    m_verticesCount = vertexData.size();

    D3D11_BLEND_DESC blendDesc{};

    blendDesc.IndependentBlendEnable = FALSE;
    blendDesc.RenderTarget[0].BlendEnable = TRUE;
    blendDesc.RenderTarget[0].SrcBlendAlpha = D3D11_BLEND_SRC_ALPHA;
    blendDesc.RenderTarget[0].SrcBlend = D3D11_BLEND_SRC_COLOR;
    blendDesc.RenderTarget[0].DestBlend = D3D11_BLEND_DEST_COLOR;
    blendDesc.RenderTarget[0].BlendOp = D3D11_BLEND_OP_ADD;
    blendDesc.RenderTarget[0].BlendOpAlpha = D3D11_BLEND_OP_ADD;
    blendDesc.RenderTarget[0].DestBlendAlpha = D3D11_BLEND_DEST_ALPHA;

    throwIfFailed(m_device->CreateBlendState(&blendDesc, &m_blendState));
}

void Engine::update(const float deltaTime)
{
    m_camera.update(deltaTime);

    const math::XMMATRIX viewMatrix = m_camera.getLookAtMatrix();
    const math::XMMATRIX projectionMatrix = math::XMMatrixPerspectiveFovLH(math::XMConvertToRadians(45.0f), m_windowWidth / static_cast<float>(m_windowHeight), 0.1f, 250.0f);

    m_sceneBuffer.data.viewMatrix = viewMatrix;
    m_sceneBuffer.data.viewProjectionMatrix = viewMatrix * projectionMatrix;

    updateConstantBuffer(m_sceneBuffer);
}

void Engine::render()
{
    // Start the Dear ImGui frame
    ImGui_ImplDX11_NewFrame();
    ImGui_ImplSDL2_NewFrame();
    ImGui::NewFrame();

    ImGui::Begin("Scene menu");
    ImGui::SliderFloat("camera mvmt speed", &m_camera.m_movementSpeed, 0.1f, 50.0f);
    ImGui::SliderFloat("camera rotation speed", &m_camera.m_rotationSpeed, 0.1f, 3.0f);

    ImGui::End();

    auto& ctx = m_deviceContext;

    constexpr std::array<float, 4> clearColor{0.2f, 0.2f, 0.2f, 1.0f};

    ctx->ClearDepthStencilView(m_depthTexture.dsv.Get(), D3D11_CLEAR_DEPTH, 1.0f, 1u);

    ctx->ClearRenderTargetView(m_renderTargetView.Get(), clearColor.data());

    const float mask[4] = {1.0f, 1.0f, 1.0f, 1.0f};
    // ctx->OMSetBlendState(m_blendState.Get(), mask, 0xffffffff);

    // Render the Geometry pass
    ctx->OMSetRenderTargets(1u, m_renderTargetView.GetAddressOf(), m_depthTexture.dsv.Get());
    ctx->RSSetViewports(1u, &m_viewport);

    bindPipeline(m_pipeline);

    constexpr uint32_t stride = sizeof(pcviz::VertexPosTexCoord);
    constexpr uint32_t offset = 0u;

    ctx->IASetVertexBuffers(0u, 1u, m_vertexBuffer.GetAddressOf(), &stride, &offset);

    ctx->VSSetConstantBuffers(0u, 1u, m_sceneBuffer.buffer.GetAddressOf());
    ctx->PSSetConstantBuffers(0u, 1u, m_sceneBuffer.buffer.GetAddressOf());
    ctx->PSSetSamplers(0u, 1u, m_wrapSampler.GetAddressOf());
    ctx->PSSetShaderResources(0u, 1u, m_texture.GetAddressOf());
    ctx->PSSetShaderResources(1u, 1u, m_depthMap.GetAddressOf());

    ctx->Draw(m_verticesCount, 0u);

    ImGui::Render();
    ImGui_ImplDX11_RenderDrawData(ImGui::GetDrawData());

    throwIfFailed(m_swapchain->Present(1u, 0u));
}
